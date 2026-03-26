" Vim syntax file for SageMath
" Language: SageMath
" Maintainer: zsm
" Latest Revision: 2026-03-26

if exists("b:current_syntax")
  finish
endif

" 加载 Python 语法作为基础
runtime! syntax/python.vim
unlet b:current_syntax

" SageMath 常量
syn keyword sageConstant ZZ QQ RR CC AA QQbar GF I pi e oo infinity Infinity
syn keyword sageConstant True False None SR

" SageMath 环和域
syn keyword sageRing PolynomialRing LaurentPolynomialRing PowerSeriesRing
syn keyword sageRing NumberField FiniteField AlgebraicField QuadraticField
syn keyword sageRing Integers Rationals RealField ComplexField Zmod
syn keyword sageRing MatrixSpace VectorSpace FreeModule

" SageMath 核心函数
syn keyword sageFunction var assume solve factor expand simplify
syn keyword sageFunction matrix vector plot show latex
syn keyword sageFunction gcd lcm mod is_prime next_prime factorial binomial
syn keyword sageFunction sqrt exp log sin cos tan asin acos atan
syn keyword sageFunction diff integrate limit sum prod

" SageMath 类
syn keyword sageClass EllipticCurve Graph DiGraph Polyhedron Partition
syn keyword sageClass SymmetricGroup AlternatingGroup PermutationGroup

" 特殊操作符
syn match sageOperator "\^\^"
syn match sageOperator "\*\*"
syn match sageOperator "\.\."

" 环生成器语法 R.<x,y> = ...
syn match sageGenerator "<[a-zA-Z_][a-zA-Z0-9_,\s]*>" contained
syn match sageRingDef "\<[A-Z][a-zA-Z0-9_]*\>\s*\.\s*<[^>]*>" contains=sageGenerator

" 高亮组
hi def link sageConstant Constant
hi def link sageRing Type
hi def link sageFunction Function
hi def link sageClass Type
hi def link sageOperator Operator
hi def link sageGenerator Special
hi def link sageRingDef Special

let b:current_syntax = "sage"
