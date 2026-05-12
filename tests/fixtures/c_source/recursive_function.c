/*
 * 递归函数样例 - Recursive Function Example
 * 用于测试递归调用检测和调用图分析
 */

/**
 * 阶乘函数 - 直接递归
 * @param n 输入整数
 * @return n 的阶乘
 */
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

/**
 * 斐波那契数列 - 直接递归（多路递归）
 * @param n 项数
 * @return 第 n 项斐波那契数
 */
int fibonacci(int n) {
    if (n <= 0) {
        return 0;
    }
    if (n == 1) {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/* 辅助函数 */
static int gcd_helper(int a, int b) {
    if (b == 0) {
        return a;
    }
    return gcd_helper(b, a % b);
}

/**
 * 最大公约数 - 辗转相除法
 * @param a 第一个整数
 * @param b 第二个整数
 * @return 最大公约数
 */
int gcd(int a, int b) {
    return gcd_helper(a, b);
}

/**
 * 间接递归示例
 * A 调用 B, B 调用 A
 */
void func_a(int n);
void func_b(int n);

void func_a(int n) {
    if (n > 0) {
        func_b(n - 1);
    }
}

void func_b(int n) {
    if (n > 0) {
        func_a(n - 1);
    }
}
