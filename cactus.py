import numpy as np

from core import Node, load
from transform import rotate, translate, scale


class CactusBuilder(Node):
    c = None
    s = None

    lb, wb = 1, 0.4
    l1, w1 = 0.5, 0.6
    l2, w2 = 0.5, 0.8
    l3, w3 = 0.5, 0.8

    # cylinder length
    dl = lb
    dl1 = dl * l1
    dl2 = dl1 * l2
    dl3 = dl2 * l3

    # cylinder width
    dw = wb
    dw1 = dw * w1
    dw2 = dw1 * w2
    dw3 = dw2 * w3

    coefs = [[dl, dw], [dl1, dw1], [dl2, dw2], [dl3, dw3]]

    vh = np.array([0, 0, 1])  # make branch vertical/horizontal
    vh_angle = 90.0  # arm angle
    around = np.array([0, 1, 0])  # rotation that separates branches
    lie = rotate(vh, vh_angle)
    stand = rotate(vh, -vh_angle)
    shader = None

    def __init__(self, shader, **uniforms):
        # cylinders dimensions
        super().__init__(**uniforms)

        # self.coefs = get_coefs()
        self.__class__.shader = shader

        ''' Base Cylinder '''

    @classmethod
    def cactus(cls, angles, rand=True, trunk_height=1.4):
        if cls.c is None or cls.s is None:
            cls.c = CactusCylinder(cls.shader)
            cls.s = CactusSphere(cls.shader)
        """ Generate cactus as a hierarchy of nodes. """
        ''' Branch 1 - sidewards '''
        b1s = cls.branch_level(angles, cls.coefs, 0, rand)

        ''' Trunk '''
        dl, dw = cls.coefs[0]
        trunk_height *= dl
        # sphere at the end of the branch
        base_sphere = Node([cls.s], translate(y=trunk_height) @ scale(dw))
        base = Node([cls.c], scale(x=dw, y=trunk_height, z=dw))
        root_node = Node([base, base_sphere, *b1s])
        return root_node

    @classmethod
    def branch_level(cls, angles, coefs, level, rand=True):
        vh = cls.lie if level % 2 == 0 else cls.stand  # make branch vertical/horizontal
        l0, w0 = coefs[level]
        l1, w1 = coefs[level + 1]
        branches = []
        for angle in angles[level]:
            # the chain is performed left to right
            transform = rotate(cls.around, angle) @ translate(y=l0) @ vh @ translate(y=l1)
            sphere = Node([cls.s], translate(y=l1) @ scale(w1))
            branch = Node([cls.c], scale(x=w1, y=l1, z=w1))
            node = Node([branch, sphere], transform)
            if rand and level == 0:
                node.apply(translate(y=-np.random.uniform(0.1, 0.7)))

            if len(angles) >= level:
                # recursive call
                b3s = cls.branch_level(angles, coefs, level + 1)
                node.add(*b3s)

            branches.append(node)

        return branches

    def __del__(self):
        del self.__class__.c, self.__class__.s


class CactusCylinder(Node):
    """ Cylinder node loading from an obj file. """

    def __init__(self, shader, **uniforms):
        super().__init__(**uniforms)
        self.add(*load('assets/cylinder.obj', shader, tex_file='assets/cactus.png'))


class CactusSphere(Node):
    """ Sphere node loading from an obj file. """

    def __init__(self, shader, **uniforms):
        super().__init__(**uniforms)
        self.add(*load('assets/sphere.obj', shader, tex_file='assets/cactus.png', k_a=[.2]*3, k_s=[.1]*3))
