import math, random
from unittest import TestCase
from . import vec2, vec3, mat3, mat4, quat


class TestVec2(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual("vec2(0, 0)", str(vec2()), )
        self.assertEqual("vec2(1, 1)", str(vec2(1)))
        self.assertEqual("vec2(5, 5)", str(vec2("5")))
        self.assertEqual("vec2(1, 2)", str(vec2(1,2)))
        self.assertEqual("vec2(1, 2)", str(vec2("1","2")))
        self.assertEqual("vec2(1, 0)", str(vec2((1,))))
        self.assertEqual("vec2(1, 2)", str(vec2((1,2))))
        self.assertEqual("vec2(1, 2)", str(vec2((1,2))))
        self.assertEqual("vec2(1, 2)", str(vec2(1,(2,))))
        self.assertEqual("vec2(1, 2)", str(vec2(("1","2"))))
        self.assertEqual("vec2(1, 0)", str(vec2([1])))
        self.assertEqual("vec2(1, 2)", str(vec2([1,2])))
        with self.assertRaises(ValueError):
            vec2(1, 2, 3)
        with self.assertRaises(ValueError):
            vec2((1, 2, 3, 4))
        with self.assertRaises(TypeError):
            vec2("bla")
        with self.assertRaises(TypeError):
            vec2({"x":23})

    def test_equal(self):
        self.assertTrue(  vec2(1) == vec2(1) )
        self.assertFalse( vec2(1) == vec2(2) )
        self.assertTrue(  vec2(1) == (1, 1) )
        self.assertFalse( vec2(1) == (1, 1, 1) )

    def test_properties(self):
        self.assertEqual(vec2(1,2).x, 1)
        self.assertEqual(vec2(1,2).y, 2)
        a = vec2()
        a.x = 5
        self.assertEqual((5,0), a)
        a.y = 6
        self.assertEqual((5, 6), a)

    def test_getitem(self):
        a = vec2(1,2)
        self.assertEqual(1, a[0])
        self.assertEqual(2, a[1])
        with self.assertRaises(IndexError):
            b = a[3]

    def test_setitem(self):
        a = vec2(0)
        a[0] = 1
        self.assertEqual(vec2(1,0), a)
        a[1] = 2
        self.assertEqual(vec2(1,2), a)
        with self.assertRaises(IndexError):
            a[3] = 1

    def test_iter(self):
        self.assertEqual([1,2], [x for x in vec2(1,2)])

    def test_abs(self):
        self.assertEqual(vec2(1,2), abs(vec2(-1,-2)))
        self.assertEqual(vec2(1,2), abs(vec2( 1,-2)))

    def test_floor(self):
        self.assertEqual(vec2(1,2), vec2(1.4,2.5).floor())
        self.assertEqual(vec2(-2,-3), vec2(-1.4,-2.5).floor())
        self.assertEqual(vec2(1,2), vec2(1.4,2.5).floored())
        self.assertEqual(vec2(-2,-3), vec2(-1.4,-2.5).floored())

    def test_round(self):
        self.assertEqual((0, 1), vec2(0.5, 0.51).round())
        self.assertEqual((0, -1), vec2(-0.5, -0.51).round())
        self.assertEqual((0.5, 0.5), vec2(0.5, 0.51).round(1))
        self.assertEqual((-0.5, -0.5), vec2(-0.5, -0.51).round(1))
        self.assertEqual((0.12346, 0.12341), vec2(0.123456, 0.1234123456789).round(5))
        self.assertEqual((0, 1), vec2(0.5, 0.51).rounded())
        self.assertEqual((0, -1), vec2(-0.5, -0.51).rounded())

    def test_add(self):
        self.assertEqual(vec2(3), vec2(1) + 2)
        self.assertEqual(vec2(3), vec2(1) + vec2(2))
        self.assertEqual(vec2(3,5), vec2(1,2) + vec2(2,3))
        self.assertEqual(vec2(3), vec2(1) + vec2(2))
        self.assertEqual(vec2(2,3), vec2(1) + [1,2])
        self.assertEqual(vec2(2,3), vec2(1) + ["1","2"])

        self.assertEqual(vec2(3), 2 + vec2(1))
        self.assertEqual(vec2(3), "2" + vec2(1))
        self.assertEqual(vec2(2,3), [1,2] + vec2(1))
        self.assertEqual(vec2(2,3), ["1","2"] + vec2(1))

        with self.assertRaises(TypeError):
            vec2() + [1]

        a = vec2(1)
        a += 1
        self.assertEqual(vec2(2), a)
        a += [1,2]
        self.assertEqual(vec2(3,4), a)

    def test_sub(self):
        self.assertEqual(vec2(1), vec2(3) - vec2(2))
        self.assertEqual(vec2(1), vec2(3) - 2)
        self.assertEqual(vec2(2,1), vec2(3) - (1,2))
        self.assertEqual(vec2(1), 3 - vec2(2))
        self.assertEqual(vec2(-1,0), (1,2) - vec2(2))

        a = vec2(1)
        a -= 2
        self.assertEqual(vec2(-1), a)
        a -= [1,2]
        self.assertEqual(vec2((-2,-3)), a)

    def test_mul(self):
        self.assertEqual(vec2(6), vec2(2) * vec2(3))
        self.assertEqual(vec2(6), vec2(2) * 3)
        self.assertEqual(vec2(2,4), vec2(2) * (1,2))
        self.assertEqual(vec2(2,4), vec2(2) * vec2(1,2))
        self.assertEqual(vec2(6), 2 * vec2(3))
        self.assertEqual(vec2(3,6), (1,2) * vec2(3))

        a = vec2(1)
        a *= 2
        self.assertEqual(vec2(2), a)
        a *= [1,2]
        self.assertEqual(vec2(2,4), a)

    def test_div(self):
        self.assertEqual(vec2(1.5), vec2(3) / vec2(2))
        self.assertEqual(vec2(1.5), vec2(3) / 2)
        self.assertEqual(vec2(2,1), vec2(2) / (1,2))
        self.assertEqual(vec2(2,1), vec2(2) / vec2((1,2)))
        self.assertEqual(vec2(1.5), 3 / vec2(2))
        self.assertEqual(vec2(.5,1), (1,2) / vec2(2))

        a = vec2(8)
        a /= 2
        self.assertEqual(vec2(4), a)
        a /= [1,2]
        self.assertEqual(vec2((4,2)), a)

    def test_mod(self):
        self.assertEqual(vec2(1,0), vec2(1,2) % 2)
        self.assertEqual(vec2(1,.5), vec2(1,3) % 2.5)

    def test_dot(self):
        self.assertEqual(2*4+3*5, vec2(2,3).dot((4,5)))
        with self.assertRaises(TypeError):
            vec2().dot((1,2,3))

    def test_rotate(self):
        self.assertEqual(vec2(-2,1), vec2(1,2).rotate_z(90).round())
        self.assertEqual(vec2(3,2), vec2(2,-3).rotate_z(90).round())

    def test_rotated(self):
        self.assertEqual(vec2(-2,1), vec2(1,2).rotated_z(90).rounded())
        self.assertEqual(vec2(3,2), vec2(2,-3).rotated_z(90).rounded())




class TestVec3(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual("vec3(0, 0, 0)", str(vec3()), )
        self.assertEqual("vec3(1, 1, 1)", str(vec3(1)))
        self.assertEqual("vec3(5, 5, 5)", str(vec3("5")))
        self.assertEqual("vec3(1, 2, 0)", str(vec3(1,2)))
        self.assertEqual("vec3(1, 2, 3)", str(vec3(1,2,3)))
        self.assertEqual("vec3(1, 2, 3)", str(vec3("1","2","3")))
        self.assertEqual("vec3(1, 0, 0)", str(vec3((1,))))
        self.assertEqual("vec3(1, 2, 0)", str(vec3((1,2))))
        self.assertEqual("vec3(1, 2, 3)", str(vec3((1,2,3))))
        self.assertEqual("vec3(1, 2, 3)", str(vec3((1,2),3)))
        self.assertEqual("vec3(1, 2, 3)", str(vec3(1,(2,3))))
        self.assertEqual("vec3(1, 2, 3)", str(vec3(1,(2,),3)))
        self.assertEqual("vec3(1, 2, 3)", str(vec3(("1","2","3"))))
        with self.assertRaises(ValueError):
            vec3(1, 2, 3, 4)
        with self.assertRaises(ValueError):
            vec3((1, 2, 3, 4))
        with self.assertRaises(TypeError):
            vec3("bla")
        with self.assertRaises(TypeError):
            vec3({"x":23})

        self.assertEqual(str(vec3([1])), "vec3(1, 0, 0)")
        self.assertEqual(str(vec3([1,2])), "vec3(1, 2, 0)")

    def test_equal(self):
        self.assertTrue(  vec3(1) == vec3(1) )
        self.assertFalse( vec3(1) == vec3(2) )
        self.assertTrue(  vec3(1) == (1,1,1) )
        self.assertFalse( vec3(1) == (1, 1) )

    def test_properties(self):
        self.assertEqual(vec3(1,2,3).x, 1)
        self.assertEqual(vec3(1,2,3).y, 2)
        self.assertEqual(vec3(1,2,3).z, 3)
        a = vec3()
        a.x = 5
        self.assertEqual((5,0,0), a)
        a.y = 6
        self.assertEqual((5, 6, 0), a)
        a.z = 7
        self.assertEqual((5, 6, 7), a)

    def test_getitem(self):
        a = vec3(1,2,3)
        self.assertEqual(1, a[0])
        self.assertEqual(2, a[1])
        self.assertEqual(3, a[2])
        with self.assertRaises(IndexError):
            a[3]

    def test_setitem(self):
        a = vec3(0)
        a[0] = 1
        self.assertEqual(vec3(1,0,0), a)
        a[1] = 2
        self.assertEqual(vec3(1,2,0), a)
        a[2] = 3
        self.assertEqual(vec3(1,2,3), a)
        with self.assertRaises(IndexError):
            a[3] = 1

    def test_iter(self):
        self.assertEqual([1,2,3], [x for x in vec3(1,2,3)])

    def test_abs(self):
        self.assertEqual(vec3(1,2,3), abs(vec3(-1,-2,-3)))
        self.assertEqual(vec3(1,2,3), abs(vec3( 1,-2, 3)))

    def test_floor(self):
        self.assertEqual(vec3(1,2,3), vec3(1.4,2.5,3.6).floor())
        self.assertEqual(vec3(-2,-3,-4), vec3(-1.4,-2.5,-3.6).floor())
        self.assertEqual(vec3(1,2,3), vec3(1.4,2.5,3.6).floored())
        self.assertEqual(vec3(-2,-3,-4), vec3(-1.4,-2.5,-3.6).floored())

    def test_round(self):
        self.assertEqual((0, 0, 1), vec3(0.49, 0.5, 0.51).round())
        self.assertEqual((0, 0, -1), vec3(-0.49, -0.5, -0.51).round())
        self.assertEqual((0.5, 0.5, 0.5), vec3(0.49, 0.5, 0.51).round(1))
        self.assertEqual((-0.5, -0.5, -0.5), vec3(-0.49, -0.5, -0.51).round(1))
        self.assertEqual((0.12346, 0.12346, 0.12341), vec3(0.123456, 0.123456789, 0.1234123456789).round(5))
        self.assertEqual((0, 0, 1), vec3(0.49, 0.5, 0.51).rounded())
        self.assertEqual((0, 0, -1), vec3(-0.49, -0.5, -0.51).rounded())

    def test_add(self):
        self.assertEqual(vec3(3), vec3(1) + 2)
        self.assertEqual(vec3(3), vec3(1) + vec3(2))
        self.assertEqual(vec3(3,5,7), vec3(1,2,3) + vec3(2,3,4))
        self.assertEqual(vec3(3), vec3(1) + vec3(2))
        self.assertEqual(vec3(2,3,4), vec3(1) + [1,2,3])
        self.assertEqual(vec3(2,3,4), vec3(1) + ["1","2","3"])

        self.assertEqual(vec3(3), 2 + vec3(1))
        self.assertEqual(vec3(3), "2" + vec3(1))
        self.assertEqual(vec3(2,3,4), [1,2,3] + vec3(1))
        self.assertEqual(vec3(2,3,4), ["1","2","3"] + vec3(1))

        with self.assertRaises(TypeError):
            vec3() + [1,2]

        a = vec3(1)
        a += 1
        self.assertEqual(vec3(2), a)
        a += [1,2,3]
        self.assertEqual(vec3(3,4,5), a)

    def test_sub(self):
        self.assertEqual(vec3(1), vec3(3) - vec3(2))
        self.assertEqual(vec3(1), vec3(3) - 2)
        self.assertEqual(vec3(2,1,0), vec3(3) - (1,2,3))
        self.assertEqual(vec3(1), 3 - vec3(2))
        self.assertEqual(vec3(-1,0,1), (1,2,3) - vec3(2))

        a = vec3(1)
        a -= 2
        self.assertEqual(vec3(-1), a)
        a -= [1,2,3]
        self.assertEqual(vec3((-2,-3,-4)), a)

    def test_mul(self):
        self.assertEqual(vec3(6), vec3(2) * vec3(3))
        self.assertEqual(vec3(6), vec3(2) * 3)
        self.assertEqual(vec3(2,4,6), vec3(2) * (1,2,3))
        self.assertEqual(vec3(2,4,6), vec3(2) * vec3(1,2,3))
        self.assertEqual(vec3(6), 2 * vec3(3))
        self.assertEqual(vec3(3,6,9), (1,2,3) * vec3(3))

        a = vec3(1)
        a *= 2
        self.assertEqual(vec3(2), a)
        a *= [1,2,3]
        self.assertEqual(vec3(2,4,6), a)

    def test_div(self):
        self.assertEqual(vec3(1.5), vec3(3) / vec3(2))
        self.assertEqual(vec3(1.5), vec3(3) / 2)
        self.assertEqual(vec3(2,1,.5), vec3(2) / (1,2,4))
        self.assertEqual(vec3(2,1,.5), vec3(2) / vec3((1,2,4)))
        self.assertEqual(vec3(1.5), 3 / vec3(2))
        self.assertEqual(vec3(.5,1,1.5), (1,2,3) / vec3(2))

        a = vec3(8)
        a /= 2
        self.assertEqual(vec3(4), a)
        a /= [1,2,4]
        self.assertEqual(vec3((4,2,1)), a)

    def test_mod(self):
        self.assertEqual(vec3(1,0,1), vec3(1,2,3) % 2)
        self.assertEqual(vec3(1,2,.5), vec3(1,2,3) % 2.5)

    def test_dot(self):
        self.assertEqual(32, vec3(1,2,3).dot((4,5,6)))
        with self.assertRaises(TypeError):
            vec3().dot((1,2))

    def test_cross(self):
        self.assertEqual((0,0,1), vec3(1,0,0).cross((0,1,0)))
        self.assertEqual((0,-1,0), vec3(1,0,0).cross((0,0,1)))
        self.assertEqual((1,0,0), vec3(0,1,0).cross((0,0,1)))
        self.assertEqual((0,0,1), vec3(1,0,0).crossed((0,1,0)))
        self.assertEqual((0,-1,0), vec3(1,0,0).crossed((0,0,1)))
        self.assertEqual((1,0,0), vec3(0,1,0).crossed((0,0,1)))

    def test_rotate(self):
        self.assertEqual(vec3(1,-3,2), vec3(1,2,3).rotate_x(90).round())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotate_y(90).round())
        self.assertEqual(vec3(-2,1,3), vec3(1,2,3).rotate_z(90).round())
        self.assertEqual(vec3(3,2,-1), vec3(2,-3,-1).rotate_z(90).round())

        self.assertEqual(vec3(1,-3,2), vec3(1,2,3).rotate_axis((1,0,0), 90).round())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotate_axis((0,1,0), 90).round())
        self.assertEqual(vec3(-2,1,3), vec3(1,2,3).rotate_axis((0,0,1), 90).round())

        self.assertEqual(vec3(2,-3,-1), vec3(1,2,3).rotate_x(90).rotate_y(90).round())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotate_x(90).rotate_y(90).rotate_z(90).round())

    def test_rotated(self):
        self.assertEqual(vec3(1,-3,2), vec3(1,2,3).rotated_x(90).rounded())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotated_y(90).rounded())
        self.assertEqual(vec3(-2,1,3), vec3(1,2,3).rotated_z(90).rounded())
        self.assertEqual(vec3(3,2,-1), vec3(2,-3,-1).rotated_z(90).rounded())

        self.assertEqual(vec3(1,-3,2), vec3(1,2,3).rotated_axis((1,0,0), 90).rounded())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotated_axis((0,1,0), 90).rounded())
        self.assertEqual(vec3(-2,1,3), vec3(1,2,3).rotated_axis((0,0,1), 90).rounded())

        self.assertEqual(vec3(2,-3,-1), vec3(1,2,3).rotated_x(90).rotated_y(90).rounded())
        self.assertEqual(vec3(3,2,-1), vec3(1,2,3).rotated_x(90).rotated_y(90).rotated_z(90).rounded())

        self.assertEqual(vec3(3,2,-1),
                vec3(1,2,3).rotated_axis((1,0,0), 90).rotated_axis((0,1,0), 90).rotated_axis((0,0,1), 90).rounded())

    """
    def test_op_speed(self):
        for i in range(100000):
            vec3(1) + vec3(2)
    """




class TestMat3(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual("mat3(1,0,0, 0,1,0, 0,0,1)", str(mat3()))
        self.assertEqual("mat3(2,0,0, 0,2,0, 0,0,2)", str(mat3(2)))
        self.assertEqual("mat3(1,2,3, 4,5,6, 7,8,9)",
                         str(mat3(1, 2, 3, 4, 5, 6, 7, 8, 9)))
        self.assertEqual("mat3(1,2,3, 4,5,6, 7,8,9)",
                         str(mat3((1, 2, 3, 4, 5, 6, 7, 8, 9))))
        self.assertEqual("mat3(1,2,3, 4,5,6, 7,8,9)",
                         str(mat3((1, 2, 3), (4, 5, 6), (7, 8, 9))))
        self.assertEqual("mat3(1,2,3, 4,5,6, 7,8,9)",
                         str(mat3(vec3(1, 2, 3), 4, (5, 6), 7, (8,), 9)))

    def test_equal(self):
        self.assertEqual(mat3(1), (1,0,0, 0,1,0, 0,0,1))

    def test_as_list(self):
        self.assertEqual([[1,2,3], [4,5,6], [7,8,9]], mat3(1,2,3,4,5,6,7,8,9).as_list_list())
        self.assertEqual([[1,4,7], [2,5,8], [3,6,9]], mat3(1,2,3,4,5,6,7,8,9).as_list_list(row_major=True))

    def test_mat4_mat3_conversion(self):
        self.assertEqual(mat4(1,2,3,0, 4,5,6,0, 7,8,9,0, 0,0,0,1), mat4(mat3(1,2,3, 4,5,6, 7,8,9)))
        self.assertEqual(mat3(1,2,3, 5,6,7, 9,10,11), mat3(mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)))

    def test_trace(self):
        self.assertEqual(15, mat3(1,2,3, 4,5,6, 7,8,9).trace())

    def test_floor(self):
        self.assertEqual(mat3(1), mat3(1.4).floor())
        self.assertEqual(mat3(1), mat3(1.5).floor())
        self.assertEqual(mat3(1), mat3(1.6).floor())
        self.assertEqual(mat3(-2), mat3(-1.4).floor())
        self.assertEqual(mat3(-2), mat3(-1.5).floor())
        self.assertEqual(mat3(-2), mat3(-1.6).floor())

    def test_round(self):
        self.assertEqual(mat3(0), mat3(0.49).round())
        self.assertEqual(mat3(0), mat3(0.5).round())
        self.assertEqual(mat3(1), mat3(0.51).round())
        self.assertEqual(mat3(0), mat3(-0.49).round())
        self.assertEqual(mat3(0), mat3(-0.5).round())
        self.assertEqual(mat3(-1), mat3(-0.51).round())
        self.assertEqual(mat3(0.5), mat3(0.49).round(1))
        self.assertEqual(mat3(0.5), mat3(0.5).round(1))
        self.assertEqual(mat3(0.5), mat3(0.51).round(1))
        self.assertEqual(mat3(-0.5), mat3(-0.49).round(1))
        self.assertEqual(mat3(-0.5), mat3(-0.5).round(1))
        self.assertEqual(mat3(-0.5), mat3(-0.51).round(1))

    def test_modulo(self):
        self.assertEqual(mat3(1,2,3, 0,1,2, 3,0,1), mat3(1,2,3, 4,5,6, 7,8,9) % 4)
        self.assertEqual(mat3(3,2,1, 0,3,2, 1,0,3), mat3(-1,-2,-3, -4,-5,-6, -7,-8,-9) % 4)

    def test_aritm(self):
        self.assertEqual(mat3(3), mat3(1)+mat3(2))
        self.assertEqual(mat3(1), mat3(2)-mat3(1))

    def test_has_rotation(self):
        self.assertFalse(mat3(1).has_rotation())
        self.assertFalse(mat3(1).scale((1, 2, 3)).has_rotation())
        self.assertTrue(mat3(1).rotate_x(0.01).has_rotation())

    def test_transpose(self):
        self.assertEqual(mat3((1,4,7, 2,5,8, 3,6,9)),
                         mat3((1,2,3, 4,5,6, 7,8,9)).transpose())
        self.assertEqual(mat3((1,4,7, 2,5,8, 3,6,9)),
                         mat3((1,2,3, 4,5,6, 7,8,9)).transposed())
        self.assertEqual(mat3((1,2,3, 4,5,6, 7,8,9)),
                         mat3((1,2,3, 4,5,6, 7,8,9)).transposed().transposed())

    def test_scalar_aritm(self):
        self.assertEqual(mat3(1) + 1, mat3((2,1,1, 1,2,1, 1,1,2)))
        self.assertEqual(mat3(1) * 3, mat3(3))
        self.assertEqual(mat3(2) - 1, mat3((1,-1,-1, -1,1,-1, -1,-1,1)))
        self.assertEqual(mat3(2) / 4, mat3(.5))

    def test_scalar_aritm_inpl(self):
        a = mat3(1)
        a += 1
        self.assertEqual(a, mat3((2,1,1, 1,2,1, 1,1,2)))
        a = mat3(1)
        a *= 3
        self.assertEqual(a, mat3(3))
        a = mat3(2)
        a -= 1
        self.assertEqual(a, mat3((1,-1,-1, -1,1,-1, -1,-1,1)))
        a = mat3(2)
        a /= 4
        self.assertEqual(a, mat3(.5))

    def test_copy_vs_inplace(self):
        m = mat3();
        m += 1;
        self.assertEqual( mat3() + 1, m)
        m = mat3();
        m -= 1;
        self.assertEqual( mat3() - 1, m)
        m = mat3();
        m *= 2;
        self.assertEqual( mat3() * 2, m)
        m = mat3();
        m /= 2;
        self.assertEqual( mat3() / 2, m)
        m = mat3(1.5);
        m %= 1;
        self.assertEqual( mat3(1.5) % 1, m)

    def test_dot(self):
        m = mat3(1,2,3, 4,5,6, 7,8,9)
        self.assertEqual(1*1+2*2+3*3+4*4+5*5+6*6+7*7+8*8+9*9, m.dot(m))

    def test_mat3_x_mat3(self):
        self.assertEqual(mat3(1*1+4*1+7*1, 2*1+5*1+8*1, 3*1+6*1+9*1,
                              1*2+4*2+7*2, 2*2+5*2+8*2, 3*2+6*2+9*2,
                              1*3+4*3+7*3, 2*3+5*3+8*3, 3*3+6*3+9*3),
                         mat3(1,2,3, 4,5,6, 7,8,9) * mat3(1,1,1, 2,2,2, 3,3,3))

    def test_mat3_x_vec3(self):
        self.assertEqual(mat3(1) * (1,2,3), vec3(1,2,3))
        self.assertEqual(mat3(2) * (1,2,3), vec3(2,4,6))

    def test_set_rotate(self):
        self.assertEqual((mat3().set_rotate_x(90) * (1, 2, 3)).round(), vec3((1, -3, 2)))
        self.assertEqual((mat3().set_rotate_y(90) * (1, 2, 3)).round(), vec3((3, 2, -1)))
        self.assertEqual((mat3().set_rotate_z(90) * (1, 2, 3)).round(), vec3((-2, 1, 3)))

        self.assertEqual((mat3().set_rotate_axis((1, 0, 0), 90) * (1, 2, 3)).round(), vec3((1, -3, 2)))
        self.assertEqual((mat3().set_rotate_axis((0, 1, 0), 90) * (1, 2, 3)).round(), vec3((3, 2, -1)))
        self.assertEqual((mat3().set_rotate_axis((0, 0, 1), 90) * (1, 2, 3)).round(), vec3((-2, 1, 3)))

    def test_rotate(self):
        self.assertEqual( (mat3().rotate_x(90) * (1,2,3)).round(), vec3((1,-3,2)) )
        self.assertEqual( (mat3().rotate_y(90).rotate_x(90) * (1,2,3)).round(), vec3((2,-3,-1)) )
        self.assertEqual( (mat3().rotate_z(90).rotate_y(90).rotate_x(90) * (1,2,3)).round(), vec3((3,2,-1)) )

        self.assertEqual( (mat3().rotate_axis((0,0,1),90).rotate_axis((0,1,0), 90).rotate_axis((1,0,0), 90)
                            * (1,2,3)).round(), vec3((3,2,-1)) )

    def test_compare_rotate_vec(self):
        v = vec3((1,2,3))
        self.assertAlmostEquals( mat3().rotate_x(90) * v, v.rotated_x(90) )
        self.assertAlmostEquals( mat3().rotate_y(90) * v, v.rotated_y(90) )
        self.assertAlmostEquals( mat3().rotate_z(90) * v, v.rotated_z(90) )

        self.assertAlmostEquals( mat3().rotate_y(-90).rotate_z(90) * v, v.rotated_z(90).rotated_y(-90) )
        self.assertAlmostEquals( mat3().rotate_x(90).rotate_y(-90).rotate_z(90) * v,
                                     v.rotated_z(90).rotated_y(-90).rotated_x(90) )

    def test_scale(self):
        self.assertEqual((mat3().init_scale(2) * (1, 2, 3)), (2, 4, 6))
        self.assertEqual((mat3().scale(2) * (1,2,3)), (2,4,6) )
        self.assertEqual((mat3().scale(2).scale(2) * (1,2,3)), (4,8,12) )
        self.assertEqual((mat3().scale(10).init_scale(2) * (1, 2, 3)), (2, 4, 6))



class TestMat4(TestCase):
    def setUp(self):
        pass

    def test_assignment(self):
        self.assertEqual("mat4(1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1)", str(mat4()))
        self.assertEqual("mat4(2,0,0,0, 0,2,0,0, 0,0,2,0, 0,0,0,2)", str(mat4(2)))
        self.assertEqual("mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)",
                         str(mat4(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)))
        self.assertEqual("mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)",
                         str(mat4((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16))))
        self.assertEqual("mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)",
                         str(mat4((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16))))
        self.assertEqual("mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)",
                         str(mat4(1, vec3(2, 3, 4), 5, 6, (7, 8), (9,), 10, 11, (12,), 13, (14, 15), 16)))

    def test_equal(self):
        self.assertEqual(mat4(1), (1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1))

    def test_trace(self):
        self.assertEqual(34, mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16).trace())

    def test_floor(self):
        self.assertEqual(mat4(1), mat4(1.4).floor())
        self.assertEqual(mat4(1), mat4(1.5).floor())
        self.assertEqual(mat4(1), mat4(1.6).floor())
        self.assertEqual(mat4(-2), mat4(-1.4).floor())
        self.assertEqual(mat4(-2), mat4(-1.5).floor())
        self.assertEqual(mat4(-2), mat4(-1.6).floor())

    def test_round(self):
        self.assertEqual(mat4(0), mat4(0.49).round())
        self.assertEqual(mat4(0), mat4(0.5).round())
        self.assertEqual(mat4(1), mat4(0.51).round())
        self.assertEqual(mat4(0), mat4(-0.49).round())
        self.assertEqual(mat4(0), mat4(-0.5).round())
        self.assertEqual(mat4(-1), mat4(-0.51).round())
        self.assertEqual(mat4(0.5), mat4(0.49).round(1))
        self.assertEqual(mat4(0.5), mat4(0.5).round(1))
        self.assertEqual(mat4(0.5), mat4(0.51).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.49).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.5).round(1))
        self.assertEqual(mat4(-0.5), mat4(-0.51).round(1))

    def test_modulo(self):
        self.assertEqual(mat4(1,2,3,0, 1,2,3,0, 1,2,3,0, 1,2,3,0),
                         mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16) % 4)
        self.assertEqual(mat4(3,2,1,0, 3,2,1,0, 3,2,1,0, 3,2,1,0),
                         mat4(-1,-2,-3,-4, -5,-6,-7,-8, -9,-10,-11,-12, -13,-14,-15,-16) % 4)

    def test_aritm(self):
        self.assertEqual(mat4(3), mat4(1)+mat4(2))
        self.assertEqual(mat4(1), mat4(2)-mat4(1))

    def test_has_translation(self):
        self.assertFalse(mat4(1).has_translation())
        self.assertFalse(mat4(2).has_translation())
        self.assertFalse(mat4(1).rotate_axis((1, 2, 3), 23.).has_translation())
        self.assertTrue(mat4(1).translate((1,2,3)).has_translation())

    def test_has_rotation(self):
        self.assertFalse(mat4(1).has_rotation())
        self.assertFalse(mat4(1).translate((1, 2, 3)).has_rotation())
        self.assertTrue(mat4(1).rotate_x(0.01).has_rotation())

    def test_transpose(self):
        self.assertEqual(mat4((1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)),
                         mat4((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)).transpose())
        self.assertEqual(mat4((1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16)),
                         mat4((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)).transposed())
        self.assertEqual(mat4((1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)),
                         mat4((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)).transposed().transposed())

    def test_scalar_aritm(self):
        self.assertEqual(mat4(1) + 1, mat4((2,1,1,1, 1,2,1,1, 1,1,2,1, 1,1,1,2)))
        self.assertEqual(mat4(1) * 3, mat4(3))
        self.assertEqual(mat4(2) - 1, mat4((1,-1,-1,-1, -1,1,-1,-1, -1,-1,1,-1, -1,-1,-1,1)))
        self.assertEqual(mat4(2) / 4, mat4(.5))

    def test_scalar_aritm_inpl(self):
        a = mat4(1)
        a += 1
        self.assertEqual(a, mat4((2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2)))
        a = mat4(1)
        a *= 3
        self.assertEqual(a, mat4(3))
        a = mat4(2)
        a -= 1
        self.assertEqual(a, mat4((1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, -1, -1, 1)))
        a = mat4(2)
        a /= 4
        self.assertEqual(a, mat4(.5))

    def test_copy_vs_inplace(self):
        m = mat4()
        m += 1
        self.assertEqual( mat4() + 1, m)
        m = mat4()
        m -= 1
        self.assertEqual( mat4() - 1, m)
        m = mat4()
        m *= 2
        self.assertEqual( mat4() * 2, m)
        m = mat4()
        m /= 2
        self.assertEqual( mat4() / 2, m)
        m = mat4(1.5)
        m %= 1
        self.assertEqual( mat4(1.5) % 1, m)

    def test_dot(self):
        m = mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16)
        self.assertEqual(1*1+2*2+3*3+4*4+5*5+6*6+7*7+8*8+9*9+10*10+11*11+12*12+13*13+14*14+15*15+16*16, m.dot(m))

    def test_mat4_x_mat4(self):
        self.assertEqual(mat4(28,32,36,40, 56,64,72,80, 84,96,108,120, 112,128,144,160),
                         mat4(1,2,3,4, 5,6,7,8, 9,10,11,12, 13,14,15,16) * mat4(1,1,1,1, 2,2,2,2, 3,3,3,3, 4,4,4,4))

    def test_mat4_x_vec3(self):
        self.assertEqual(mat4(1) * (1,2,3), vec3(1,2,3))
        self.assertEqual(mat4(2) * (1,2,3), vec3(2,4,6))

    def test_set_translate(self):
        self.assertEqual( (mat4().set_translate((1,2,3)) * (3,3,3)), (4,5,6))
        with self.assertRaises(TypeError):
            mat4().set_translate(1)
        with self.assertRaises(TypeError):
            mat4().set_translate((1,2))

    def test_translate(self):
        self.assertEqual( (mat4().translate((1,2,3)) * (3,3,3)), (4,5,6) )
        self.assertEqual( (mat4().translate((1,2,3)).translate((1,2,3)) * (3,3,3)), (5,7,9) )

    def test_set_rotate(self):
        self.assertEqual((mat4().set_rotate_x(90) * (1, 2, 3)).round(), vec3((1, -3, 2)))
        self.assertEqual((mat4().set_rotate_y(90) * (1, 2, 3)).round(), vec3((3, 2, -1)))
        self.assertEqual((mat4().set_rotate_z(90) * (1, 2, 3)).round(), vec3((-2, 1, 3)))

        self.assertEqual((mat4().set_rotate_axis((1, 0, 0), 90) * (1, 2, 3)).round(), vec3((1, -3, 2)))
        self.assertEqual((mat4().set_rotate_axis((0, 1, 0), 90) * (1, 2, 3)).round(), vec3((3, 2, -1)))
        self.assertEqual((mat4().set_rotate_axis((0, 0, 1), 90) * (1, 2, 3)).round(), vec3((-2, 1, 3)))

    def test_rotate(self):
        self.assertEqual( (mat4().rotate_x(90) * (1,2,3)).round(), vec3((1,-3,2)) )
        self.assertEqual( (mat4().rotate_y(90).rotate_x(90) * (1,2,3)).round(), vec3((2,-3,-1)) )
        self.assertEqual( (mat4().rotate_z(90).rotate_y(90).rotate_x(90) * (1,2,3)).round(), vec3((3,2,-1)) )

        self.assertEqual( (mat4().rotate_axis((0,0,1),90).rotate_axis((0,1,0), 90).rotate_axis((1,0,0), 90)
                            * (1,2,3)).round(), vec3((3,2,-1)) )

    def test_compare_rotate_vec(self):
        v = vec3((1,2,3))
        self.assertAlmostEquals( mat4().rotate_x(90) * v, v.rotated_x(90) )
        self.assertAlmostEquals( mat4().rotate_y(90) * v, v.rotated_y(90) )
        self.assertAlmostEquals( mat4().rotate_z(90) * v, v.rotated_z(90) )

        self.assertAlmostEquals( mat4().rotate_y(-90).rotate_z(90) * v, v.rotated_z(90).rotated_y(-90) )
        self.assertAlmostEquals( mat4().rotate_x(90).rotate_y(-90).rotate_z(90) * v,
                                     v.rotated_z(90).rotated_y(-90).rotated_x(90) )

    def test_scale(self):
        self.assertEqual((mat4().init_scale(2) * (1, 2, 3)), (2, 4, 6))
        self.assertEqual( (mat4().scale(2) * (1,2,3)), (2,4,6) )
        self.assertEqual( (mat4().scale(2).scale(2) * (1,2,3)), (4,8,12) )
        self.assertEqual((mat4().scale(10).init_scale(2) * (1, 2, 3)), (2, 4, 6))

    def test_position(self):
        self.assertEqual( mat4().translate((1,2,3)).position(), (1,2,3))
        self.assertEqual( mat4().rotate_x(90).translate((1,2,3)).position(), (1,-3,2))
        self.assertEqual( mat4().translate((1,2,3)).rotate_x(90).position(), (1,2,3))
        a = mat4().rotate_x(90).translate((1,2,3))
        self.assertEqual(a.position(), a * (0,0,0))







class TestQuat(TestCase):
    def setUp(self):
        self.r = random.Random(23)
        pass

    def test_assignment(self):
        self.assertEqual("quat(0, 0, 0, 1)", str(quat()), )
        self.assertEqual("quat(1, 2, 3, 4)", str(quat(1,2,3,4)) )
        with self.assertRaises(TypeError):
            quat(1,2,3)
        with self.assertRaises(TypeError):
            quat((1,2,3))
        with self.assertRaises(TypeError):
            quat((1,2,3),4,5)
        with self.assertRaises(TypeError):
            quat("bla")
        with self.assertRaises(TypeError):
            quat({"x":23})

    def test_equal(self):
        self.assertTrue(  quat() == (0,0,0,1) )
        self.assertFalse( quat() == (0,0,0) )
        self.assertFalse( quat() == (0,0,0,0,0) )
        self.assertTrue(  quat(1,2,3,4) == (1,2,3,4) )

    def test_properties(self):
        self.assertEqual(quat(1,2,3,4).x, 1)
        self.assertEqual(quat(1,2,3,4).y, 2)
        self.assertEqual(quat(1,2,3,4).z, 3)
        self.assertEqual(quat(1,2,3,4).w, 4)
        a = quat()
        a.x = 5
        self.assertEqual((5,0,0,1), a)
        a.y = 6
        self.assertEqual((5,6,0,1), a)
        a.z = 7
        self.assertEqual((5,6,7,1), a)
        a.w = 8
        self.assertEqual((5,6,7,8), a)

    def test_getitem(self):
        a = quat(1,2,3,4)
        self.assertEqual(1, a[0])
        self.assertEqual(2, a[1])
        self.assertEqual(3, a[2])
        self.assertEqual(4, a[3])
        with self.assertRaises(IndexError):
            b = a[4]

    def test_setitem(self):
        a = quat()
        a[0] = 1
        self.assertEqual(quat(1,0,0,1), a)
        a[1] = 2
        self.assertEqual(quat(1,2,0,1), a)
        a[2] = 3
        self.assertEqual(quat(1,2,3,1), a)
        a[3] = 4
        self.assertEqual(quat(1,2,3,4), a)
        with self.assertRaises(IndexError):
            a[4] = 1

    def test_iter(self):
        self.assertEqual([1,2,3,4], [x for x in quat(1,2,3,4)])

    def test_abs(self):
        self.assertEqual(quat(1,2,3,4), abs(quat(-1,-2,-3,-4)))
        self.assertEqual(quat(1,2,3,4), abs(quat( 1,-2, 3,-4)))

    def test_floor(self):
        self.assertEqual(quat(1,2,3,4), quat(1.4,2.5,3.6,4.7).floor())
        self.assertEqual(quat(-2,-3,-4,-5), quat(-1.4,-2.5,-3.6,-4.7).floor())
        self.assertEqual(quat(1,2,3,4), quat(1.4,2.5,3.6,4.7).floored())
        self.assertEqual(quat(-2,-3,-4,-5), quat(-1.4,-2.5,-3.6,-4.7).floored())

    def test_round(self):
        self.assertEqual((0, 0, 1, 0), quat(0.49, 0.5, 0.51, 0).round())
        self.assertEqual((0, 0, -1, 0), quat(-0.49, -0.5, -0.51, 0).round())
        self.assertEqual((0.5, 0.5, 0.5, 0), quat(0.49, 0.5, 0.51, 0).round(1))
        self.assertEqual((-0.5, -0.5, -0.5, 0), quat(-0.49, -0.5, -0.51, 0).round(1))
        self.assertEqual((0.12346, 0.12346, 0.12341, 0), quat(0.123456, 0.123456789, 0.1234123456789, 0).round(5))
        self.assertEqual((0, 0, 1, 0), quat(0.49, 0.5, 0.51, 0).rounded())
        self.assertEqual((0, 0, -1, 0), quat(-0.49, -0.5, -0.51, 0).rounded())

    def test_length(self):
        self.assertAlmostEquals(1., quat(1,0,0,0).length())
        self.assertAlmostEquals(math.sqrt(2.), quat(1,1,0,0).length())
        self.assertAlmostEquals(1., quat(1,2,3,4).normalized().length())

    def test_dot(self):
        self.assertEqual(60, quat(1,2,3,4).dot((4,5,6,7)))
        with self.assertRaises(TypeError):
            quat().dot((1,2))

    def _compare_quat_mat(self, q, m, prec=4):
        self.assertEqual(q.rounded(prec), m.as_quat().rounded(prec))
        self.assertEqual(q.as_mat3().rounded(prec), m.rounded(prec))

    def test_mat_conversion(self):
        self.assertEqual(quat(), mat3().as_quat())
        self._compare_quat_mat(quat((1,0,0), 90), mat3().set_rotate_x(90.))
        self._compare_quat_mat(quat((0,1,0), 90), mat3().set_rotate_y(90.))
        self._compare_quat_mat(quat((0,0,1), 90), mat3().set_rotate_z(90.))
        for i in range(100):
            axis = vec3(self.r.gauss(0,1), self.r.gauss(0,1), self.r.gauss(0,1)).normalize()
            deg = self.r.uniform(-119, 119)
            self._compare_quat_mat(quat(axis, deg), mat3().set_rotate_axis(axis, deg))
            self._compare_quat_mat(quat(-axis, deg), mat3().set_rotate_axis(-axis, deg) )

    def test_mat_conversion_concat(self):
        for i in range(100):
            q = quat()
            m = mat3()
            # TODO: more than one transform is way off
            for j in range(1):
                axis = vec3(self.r.gauss(0,1), self.r.gauss(0,1), self.r.gauss(0,1)).normalize()
                deg = self.r.uniform(-180/5, 180/5)
                q.rotate_axis(axis, deg)
                m.rotate_axis(axis, deg)
                qm = q.as_mat3().round(3)
                mm = m.rounded(3)
                diff = abs(sum(qm - mm))
                if diff > .1:
                    self.assertEqual(qm, mm)
                self.assertLess(diff, 0.1)
            #self._compare_quat_mat( q, m, 8)

    def _compare_mat3_quat_rotation(self, axis, deg):
        self.assertEqual(mat3().set_rotate_axis(axis, deg).round(4),
                         quat().set_rotate_axis(axis, deg).as_mat3().round(4))
        self.assertEqual(mat3().set_rotate_axis(axis, deg).round(4),
                         (mat3() * quat().set_rotate_axis(axis, deg)).round(4))
        self.assertEqual(mat3().set_rotate_axis(axis, deg).rotate_axis(axis,deg).round(4),
                         (mat3() * quat().set_rotate_axis(axis, deg).rotate_axis(axis, deg)).round(4))

    def test_rotate(self):
        self.assertEqual(quat().set_rotate_axis((1,2,3), 4), quat((1, 2, 3), 4))
        self.assertEqual(mat3().set_rotate_axis((1,0,0), 0).round(),
                         quat().set_rotate_axis((1,0,0), 0).as_mat3().round())
        self.assertEqual(mat3().set_rotate_axis((1,0,0), 90).round(),
                         quat().set_rotate_axis((1,0,0), 90).as_mat3().round())
        for i in range(100):
            axis = vec3(self.r.gauss(0, 1), self.r.gauss(0, 1), self.r.gauss(0, 1)).normalize()
            deg = self.r.uniform(-360, 360)
            self._compare_mat3_quat_rotation(axis, deg)

    def test_rotate_to(self):
        self.assertEqual(quat().set_rotate_axis((1, 0, 0), 90), vec3(0, 0, -1).get_rotation_to((0, 1, 0)))
        self.assertEqual(quat().set_rotate_axis((0, 1, 0), 90), vec3(0, 0, 1).get_rotation_to((1, 0, 0)))
        self.assertEqual(quat().set_rotate_axis((0, 0, 1), 90), vec3(0, 1, 0).get_rotation_to((-1, 0, 0)))

    def test_rotate_to_mat(self):
        cur = vec3(0,1,0)
        goal = vec3(1,0,0)
        v = cur.get_rotation_to(goal).as_mat3() * cur
        self.assertEqual(goal.rounded(3), v.rounded(3))
