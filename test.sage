# test.sage - SageMath 测试文件

# 基础数学对象
R = PolynomialRing(ZZ, 'x')
x = R.gen()

# 多项式运算
p = x^2 + 2*x + 1
print("多项式:", p)
print("因式分解:", p.factor())

# 矩阵运算
M = matrix(QQ, [[1, 2], [3, 4]])
print("矩阵:", M)
print("行列式:", M.det())

# 符号计算
var('y')
expr = (y^2 + 2*y + 1).factor()
print("符号表达式:", expr)
