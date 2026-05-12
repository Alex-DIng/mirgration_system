/*
 * 简单函数样例 - Simple Function Example
 * 用于测试基本的 C 语言解析功能
 */

/**
 * 两数相加
 * @param a 第一个整数
 * @param b 第二个整数
 * @return 两数之和
 */
int add(int a, int b) {
    return a + b;
}

/**
 * 两数相减
 * @param a 被减数
 * @param b 减数
 * @return 差值
 */
int subtract(int a, int b) {
    return a - b;
}

/**
 * 主函数 - 程序入口
 */
int main() {
    int x = 10;
    int y = 5;

    int sum = add(x, y);
    int diff = subtract(x, y);

    return sum - diff;
}
