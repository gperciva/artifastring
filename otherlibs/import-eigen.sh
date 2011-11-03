#!/bin/sh

DIR=$1/Eigen
OUT=Eigen

mkdir -p Eigen
mkdir -p Eigen/src/plugins/
mkdir -p Eigen/src/misc/
mkdir -p Eigen/src/Core/util/
mkdir -p Eigen/src/Core/arch/SSE/
mkdir -p Eigen/src/Core/arch/Default/
mkdir -p Eigen/src/LU/

cp $DIR/Core $OUT
cp $DIR/LU $OUT

cp $1/COPYING* $OUT
echo "imported from http://http://eigen.tuxfamily.org/" > $OUT/imported-project.txt

### utils
for a in DisableStupidWarnings.h Macros.h MKL_support.h \
	Constants.h ForwardDeclarations.h Meta.h XprHelper.h \
	StaticAssert.h Memory.h BlasUtil.h
do
	cp $DIR/src/Core/util/$a $OUT/src/Core/util/
done

### ()
for a in BlockMethods.h CommonCwiseUnaryOps.h \
	CommonCwiseBinaryOps.h MatrixCwiseUnaryOps.h \
	MatrixCwiseBinaryOps.h
do
	cp $DIR/src/plugins/$a $OUT/src/plugins/
done

### ()
cp -r $DIR/src/Core/* $OUT/src/Core/
cp -r $DIR/src/plugins/* $OUT/src/plugins/
cp -r $DIR/src/misc/* $OUT/src/misc/
cp -r $DIR/src/LU/* $OUT/src/LU/

### arch/SSE
for a in PacketMath.h MathFunctions.h Complex.h
do
	cp $DIR/src/Core/arch/SSE/$a $OUT/src/Core/arch/SSE/
done

### arch/Default
for a in Settings.h
do
	cp $DIR/src/Core/arch/Default/$a $OUT/src/Core/arch/Default/
done


