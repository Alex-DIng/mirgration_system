/*
 * 简单函数样例 - 预期 Java 输出
 * Simple Function Example - Expected Java Output
 */

package com.migration.sample;

/**
 * 简单数学运算工具类
 * Simple Math Utility Class
 */
public class SimpleFunctionSample {

    /**
     * 两数相加
     * @param a 第一个整数
     * @param b 第二个整数
     * @return 两数之和
     */
    public int add(int a, int b) {
        return a + b;
    }

    /**
     * 两数相减
     * @param a 被减数
     * @param b 减数
     * @return 差值
     */
    public int subtract(int a, int b) {
        return a - b;
    }

    /**
     * 主函数 - 程序入口
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        SimpleFunctionSample sample = new SimpleFunctionSample();

        int x = 10;
        int y = 5;

        int sum = sample.add(x, y);
        int diff = sample.subtract(x, y);

        System.out.println("Result: " + (sum - diff));
    }
}
