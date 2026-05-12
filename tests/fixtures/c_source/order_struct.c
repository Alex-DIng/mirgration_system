/*
 * 证券订单结构体样例 - Securities Order Struct Example
 * 用于测试结构体解析和 Java Entity 转换
 */

#include <stdio.h>
#include <string.h>

/* 订单类型枚举 */
typedef enum {
    ORDER_TYPE_BUY = 1,   /* 买入 */
    ORDER_TYPE_SELL = 2   /* 卖出 */
} OrderType;

/* 订单状态枚举 */
typedef enum {
    ORDER_STATUS_PENDING = 0,    /* 待报 */
    ORDER_STATUS_SUBMITTED = 1,  /* 已报 */
    ORDER_STATUS_FILLED = 2,     /* 成交 */
    ORDER_STATUS_CANCELLED = 3,  /* 撤单 */
    ORDER_STATUS_REJECTED = 4    /* 废单 */
} OrderStatus;

/* 证券订单结构体 */
typedef struct {
    int order_id;           /* 订单 ID */
    OrderType type;         /* 订单类型 */
    char stock_code[16];    /* 证券代码 */
    char stock_name[32];    /* 证券名称 */
    int quantity;           /* 委托数量 */
    double price;           /* 委托价格 */
    OrderStatus status;     /* 订单状态 */
    long timestamp;         /* 时间戳 */
} SecuritiesOrder;

/* 订单管理函数 */
SecuritiesOrder* create_order(
    int order_id,
    OrderType type,
    const char* stock_code,
    int quantity,
    double price
) {
    SecuritiesOrder* order = (SecuritiesOrder*)malloc(sizeof(SecuritiesOrder));
    if (order == NULL) {
        return NULL;
    }

    order->order_id = order_id;
    order->type = type;
    strncpy(order->stock_code, stock_code, 15);
    order->stock_code[15] = '\0';
    order->quantity = quantity;
    order->price = price;
    order->status = ORDER_STATUS_PENDING;
    order->timestamp = get_current_timestamp();

    return order;
}

int validate_order(SecuritiesOrder* order) {
    if (order == NULL) {
        return 0;
    }
    if (order->quantity <= 0) {
        return 0;
    }
    if (order->price < 0.0) {
        return 0;
    }
    return 1;
}

int submit_order(SecuritiesOrder* order) {
    if (!validate_order(order)) {
        return -1;
    }
    order->status = ORDER_STATUS_SUBMITTED;
    return 0;
}
