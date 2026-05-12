/*
 * 证券订单实体类 - 预期 Java 输出
 * Securities Order Entity - Expected Java Output
 */

package com.migration.securities;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 订单类型枚举
 */
public enum OrderType {
    BUY(1),    // 买入
    SELL(2);   // 卖出

    private final int code;

    OrderType(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }

    public static OrderType fromCode(int code) {
        for (OrderType type : values()) {
            if (type.getCode() == code) {
                return type;
            }
        }
        throw new IllegalArgumentException("Unknown order type code: " + code);
    }
}

/**
 * 订单状态枚举
 */
public enum OrderStatus {
    PENDING(0),      // 待报
    SUBMITTED(1),    // 已报
    FILLED(2),       // 成交
    CANCELLED(3),    // 撤单
    REJECTED(4);     // 废单

    private final int code;

    OrderStatus(int code) {
        this.code = code;
    }

    public int getCode() {
        return code;
    }

    public static OrderStatus fromCode(int code) {
        for (OrderStatus status : values()) {
            if (status.getCode() == code) {
                return status;
            }
        }
        throw new IllegalArgumentException("Unknown order status code: " + code);
    }
}

/**
 * 证券订单实体类
 * 对应 C 语言 SecuritiesOrder 结构体
 */
@Entity
@Table(name = "securities_order")
public class SecuritiesOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "order_id")
    private Integer orderId;

    @Enumerated(EnumType.ORDINAL)
    @Column(name = "order_type", nullable = false)
    private OrderType type;

    @Column(name = "stock_code", length = 16, nullable = false)
    private String stockCode;

    @Column(name = "stock_name", length = 32)
    private String stockName;

    @Column(name = "quantity", nullable = false)
    private Integer quantity;

    @Column(name = "price", nullable = false, precision = 10, scale = 2)
    private Double price;

    @Enumerated(EnumType.ORDINAL)
    @Column(name = "status", nullable = false)
    private OrderStatus status;

    @Column(name = "timestamp")
    private Long timestamp;

    // ==================== 默认构造函数 ====================

    public SecuritiesOrder() {
        this.status = OrderStatus.PENDING;
    }

    // ==================== 全参构造函数 ====================

    public SecuritiesOrder(Integer orderId, OrderType type, String stockCode,
                           String stockName, Integer quantity, Double price,
                           OrderStatus status, Long timestamp) {
        this.orderId = orderId;
        this.type = type;
        this.stockCode = stockCode;
        this.stockName = stockName;
        this.quantity = quantity;
        this.price = price;
        this.status = status;
        this.timestamp = timestamp;
    }

    // ==================== Getter/Setter 方法 ====================

    public Integer getOrderId() {
        return orderId;
    }

    public void setOrderId(Integer orderId) {
        this.orderId = orderId;
    }

    public OrderType getType() {
        return type;
    }

    public void setType(OrderType type) {
        this.type = type;
    }

    public String getStockCode() {
        return stockCode;
    }

    public void setStockCode(String stockCode) {
        this.stockCode = stockCode;
    }

    public String getStockName() {
        return stockName;
    }

    public void setStockName(String stockName) {
        this.stockName = stockName;
    }

    public Integer getQuantity() {
        return quantity;
    }

    public void setQuantity(Integer quantity) {
        this.quantity = quantity;
    }

    public Double getPrice() {
        return price;
    }

    public void setPrice(Double price) {
        this.price = price;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public void setStatus(OrderStatus status) {
        this.status = status;
    }

    public Long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Long timestamp) {
        this.timestamp = timestamp;
    }

    // ==================== 业务方法 ====================

    /**
     * 验证订单参数
     * @return 是否有效
     */
    public boolean validate() {
        return this.quantity != null && this.quantity > 0
            && this.price != null && this.price >= 0.0;
    }

    /**
     * 提交订单
     * @return 提交结果
     */
    public boolean submit() {
        if (!validate()) {
            return false;
        }
        this.status = OrderStatus.SUBMITTED;
        return true;
    }

    // ==================== equals/hashCode ====================

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SecuritiesOrder that = (SecuritiesOrder) o;
        return orderId != null && orderId.equals(that.orderId);
    }

    @Override
    public int hashCode() {
        return orderId != null ? orderId.hashCode() : 0;
    }

    @Override
    public String toString() {
        return "SecuritiesOrder{" +
                "orderId=" + orderId +
                ", type=" + type +
                ", stockCode='" + stockCode + '\'' +
                ", quantity=" + quantity +
                ", price=" + price +
                ", status=" + status +
                '}';
    }
}
