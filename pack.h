#ifndef _NET_PACK_H_
#define _NET_PACK_H_

#include <iostream>
#include <stdint.h>
#include <queue>
#include <map>
#include <malloc.h>
#include <string.h>

using namespace std;

struct netpack {
    int id;
    int size;
    uint8_t *data;
};

struct uncomplete {
    struct netpack pack;
    int read;
    int header;
};

queue <struct netpack *> send_queue;
queue <struct netpack *> recv_queue;
map <int, uncomplete *> uc_map;

static inline void write_size(uint8_t *buf, int len) {
    buf[0] = (len >> 8) & 0xff;
    buf[1] = len & 0xff;
}

static void push_to_send_queue(uint8_t *buf, int fd, int size){
    struct netpack *pack = (struct netpack *)malloc(sizeof(struct netpack));
    pack->id = fd;
    pack->size = size;
    pack->data = buf;

    send_queue.push(pack);
}

static int pack(const char *data, int fd) {
    size_t len = strlen(data);
    if (len > 0x10000) {
        return 1;
    }

    uint8_t *buf = (uint8_t *)malloc(len + 2);
    write_size(buf, len);
    memcpy(buf+2, data, len);

    push_to_send_queue(buf, fd, len+2);

    return 0;
}

static struct netpack * get_msg() {
    return send_queue.front();
}

static void pop_msg() {
    struct netpack *pack = get_msg();
    send_queue.pop();
    free(pack->data);
    free(pack);
}

static inline int read_size (uint8_t *buf) {
    return (int)buf[0] << 8 | (int)buf[1];
}

static struct uncomplete * find_uncomplete_msg(int fd) {
    map<int, uncomplete *>::iterator iter =  uc_map.find(fd);
    if (iter != uc_map.end()) {
        return iter->second;
    }else{
        return NULL;
    }
}

static struct uncomplete * save_uncomplete(int fd, int pack_size, int size) {
    struct uncomplete *uc = (struct uncomplete *) malloc (sizeof(struct uncomplete));
    uc->read = size;
    uc->pack.id = fd;
    uc->pack.size = pack_size;
    uc_map[fd] = uc;
    return uc;
}

static void push_to_recv_queue(uint8_t *buf, const int fd, int size) {
    struct netpack *pack = (struct netpack *) malloc (sizeof(struct netpack));
    pack->id = fd;
    pack->size = size;
    pack->data = (uint8_t *) malloc (size);
    memcpy(pack->data, buf, size);
    recv_queue.push(pack);
}

static void push_more(uint8_t *buf, int fd, int size) {
    if (1 == size) {
        struct uncomplete *uc = save_uncomplete(fd, 0, 0);
        uc->header = *buf;
        return;
    }

    int pack_size = read_size(buf);
    size -= 2;
    buf += 2;
    if (pack_size > size) {
        struct uncomplete *uc = save_uncomplete(fd, pack_size, size);
        uc->pack.data = (uint8_t *) malloc (pack_size);
        memcpy(uc->pack.data, buf, size);
        return;
    }

    push_to_recv_queue(buf, fd, pack_size);
    size -= pack_size;
    if (size) {
        push_more(buf+pack_size, fd, size);
    }
}

static int filter_data(uint8_t *buf, const int fd, int size) {
    struct uncomplete *uc = find_uncomplete_msg(fd);
    if (uc){
        if (1 == uc->read) {
            int pack_size = buf[0];
            pack_size |= (int)uc->header << 8;
            --size;
            ++buf;
            uc->pack.data = (uint8_t *) malloc (pack_size);
            uc->pack.size = pack_size;
            uc->header = 0;
        }
        
        int need = uc->pack.size - uc->read;
        if (size < need) {
           memcpy(uc->pack.data + uc->read, buf, size); 
           uc->read += size;
           return 1;
        }

        memcpy(uc->pack.data + uc->read, buf, need);
        push_to_recv_queue(uc->pack.data, uc->pack.id, uc->pack.size);
        free(uc->pack.data);
        free(uc);
        uc_map.erase(fd);
        if (size == need) {
            return 5;
        }
        //push more
        buf += need;
        size -= need;
        push_more(buf+need, fd, size-need);
        return 2;
    }else {
        if (1 == size) {
            uc = save_uncomplete(fd, 0, 0);
            uc->header = *buf;
            return 1;    
        }

        int pack_size = read_size((uint8_t *)buf);
        size -= 2;
        buf += 2;
        if (size < pack_size) {
            uc = save_uncomplete(fd, pack_size, size);
            uc->pack.data = (uint8_t *) malloc (pack_size);
            memcpy(uc->pack.data, buf, size);
            return 1;
        }

        size -= pack_size;
        push_to_recv_queue(buf, fd, pack_size);
        if (size == 0) {
            return 5;
        }
        //push more
        buf += pack_size;
        size -+ pack_size;
        push_more(buf, fd, size);
        return 2;
    }
}


#endif
