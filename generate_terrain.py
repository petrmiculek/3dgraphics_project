# standard library
from os.path import exists
from sys import stderr

# external libraries
import numpy as np
import matplotlib.pyplot as plt


# local imports
# -

# perlin noise code adapted from: https://github.com/pvigier/perlin-numpy
def generate_perlin_noise_2d(shape, res):
    def smoothen(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    # make shape a nearest power of 2
    shape_orig = shape
    shape = (2 ** int(np.ceil(np.log2(shape[0]))), 2 ** int(np.ceil(np.log2(shape[1]))))

    res_x, res_y = res
    x, y = shape[0], shape[1]
    dx, dy = res_x / x, res_y / y
    nx, ny = x // res_x, y // res_y
    if x % res_x != 0:
        nx += 1
    if y % res_y != 0:
        ny += 1

    grid = np.mgrid[0:res_x:dx, 0:res_y:dy].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res_x + 1, res_y + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(nx, 0).repeat(ny, 1)[:x, :y]
    g10 = gradients[1:, 0:-1].repeat(nx, 0).repeat(ny, 1)[:x, :y]
    g01 = gradients[0:-1, 1:].repeat(nx, 0).repeat(ny, 1)[:x, :y]
    g11 = gradients[1:, 1:].repeat(nx, 0).repeat(ny, 1)[:x, :y]
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = smoothen(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    p = np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)[:shape_orig[0], :shape_orig[1]]
    return p


def generate_fractal_noise_2d(shape, res, octaves=1, persistence=0.4, show=False):
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    plt.subplots(1, octaves + 1, figsize=((2 + octaves) * 5, 5))
    for p in range(octaves):
        perlin = generate_perlin_noise_2d(shape, (frequency * res[0], frequency * res[1]))
        noise += amplitude * perlin
        frequency *= 2
        amplitude *= persistence
        plt.subplot(1, octaves + 1, p + 1)
        plt.imshow(perlin, cmap='gray')
        plt.title(f'Octave {p + 1} {shape} {frequency * res[0]} {frequency * res[1]}')

    plt.subplot(1, octaves + 1, octaves + 1)
    plt.imshow(noise, cmap='gray')
    plt.title('Sum')
    if show:
        plt.show()

    # delete figure
    plt.close()

    return noise


def generate_terrain(dim=100,
                     crater_center=None,
                     crater_radius=30,
                     crater_height=100,
                     hole_radius=10,
                     noise_amplitude=50):
    # base terrain grid
    terrain = np.zeros((dim, dim), dtype=np.float32)

    # perlin noise
    terrain += noise_amplitude * generate_fractal_noise_2d(terrain.shape, res=(1, 1),
                                                           octaves=5, persistence=0.3)
    lava_height, lava, terrain = generate_crater(crater_center, crater_height, crater_radius,
                                                 hole_radius, terrain)

    return terrain, lava, lava_height


def generate_crater(crater_center, crater_height, crater_radius, hole_radius, terrain):
    dim = terrain.shape[0]
    r_big = int(crater_radius * 4)

    if crater_center is None:
        # choose best position for the crater - highest point in the terrain
        # we assume that there is only one such point
        crater_center = np.unravel_index(np.argmax(terrain), terrain.shape)

    # if crater is too close to the edge, move it towards the center
    crater_center = np.clip(crater_center, r_big, dim - r_big)
    print(f'Crater center: {crater_center}')
    ''' Crater generation - initial version with for-loops (UNUSED) '''
    if False:
        # gaussian crater
        for i in range(crater_center[0] - r_big, crater_center[0] + r_big):
            for j in range(crater_center[1] - r_big, crater_center[1] + r_big):
                if i < 0 or i >= dim or j < 0 or j >= dim:
                    continue
                dist = np.sqrt((i - crater_center[0]) ** 2 + (j - crater_center[1]) ** 2)
                terrain[i, j] += crater_height * np.exp(-dist / crater_radius)

        # hole in crater
        for i in range(crater_center[0] - crater_radius, crater_center[0] + crater_radius):
            for j in range(crater_center[1] - crater_radius, crater_center[1] + crater_radius):
                dist = np.sqrt((i - crater_center[0]) ** 2 + (j - crater_center[1]) ** 2)
                if dist < hole_radius:
                    terrain[i, j] = 0

    ''' Crater generation - vectorized version '''
    # precompute distances from crater center
    x_low, x_high = crater_center[0] - r_big, crater_center[0] + r_big
    y_low, y_high = crater_center[1] - r_big, crater_center[1] + r_big
    dists = np.sqrt((np.arange(x_low, x_high)[:, None] - crater_center[0]) ** 2 + (
            np.arange(y_low, y_high)[None, :] - crater_center[1]) ** 2)
    # compute crater height
    crater = crater_height * np.exp(-dists / crater_radius)
    # shift to start at 0
    crater -= np.min(crater)
    # between hole_radius and hole_radius + 5
    crater_edge_idx = np.logical_and(dists > hole_radius, dists < hole_radius + 5)
    crater_inside = np.argwhere(
        dists < hole_radius)  # needs clamping of the range to fit in the ground, assume this is not a problem for now
    # hole in crater
    crater[dists < hole_radius] = 0
    # terrain[min_x:max_x, min_y:max_y] += crater
    terrain[x_low:x_high, y_low:y_high] += crater
    # shift ground to positive values
    shift = np.min(terrain)
    terrain += shift
    # crater properties are calculated based on the terrain with the crater placed
    crater_placed = terrain[x_low:x_high, y_low:y_high]
    crater_edge_placed = crater_placed[crater_edge_idx]
    lava = crater_inside + np.array([x_low, y_low])
    lava_height = np.mean(crater_edge_placed) - 0.5  # safety margin
    return lava_height, lava, terrain


def save_i(path, data=None, overwrite=False, **data_dict):
    """ Save data to npz file """
    if exists(path) and not overwrite:
        print(f'file already exists ({path})', file=stderr)
        print(f'remove existing and run again: rm -f {path}')
    else:
        if data is not None:
            data_dict.update({'data': data})
        np.savez(path, **data_dict)
        print(f'Saved to: {path}.npz')


def plot_terrain(ground):
    # plot crater 3d surface
    dim_x, dim_y = ground.shape
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = np.arange(0, dim_x, 1)
    y = np.arange(0, dim_y, 1)
    X, Y = np.meshgrid(x, y)
    ax.plot_surface(X, Y, ground, cmap='gray')
    # xyz limit 0 to 100
    ax.set_xlim(0, dim_x)
    ax.set_ylim(0, dim_y)
    # ax.set_zlim(0, 100)

    plt.tight_layout()
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    # set manual seed - always makes the same crater
    np.random.seed(98)

    show_plots = False
    if not show_plots:
        plt.ioff()
        # plt.ion()

    ''' Terrain generation '''
    dim = 300
    terrain, crater_inside, crater_edge_height = generate_terrain(dim=dim,
                                                                  crater_height=40,
                                                                  hole_radius=10,
                                                                  crater_radius=30,
                                                                  noise_amplitude=70)

    # compute normals
    grad = np.gradient(terrain)
    grad_x, grad_z = grad

    # normals
    grad_y = np.ones_like(grad_x)
    normals_grid = np.stack((grad_x, grad_y, grad_z), axis=2)
    normals_grid = normals_grid / np.linalg.norm(normals_grid, axis=2)[:, :, None]
    normals_grid = normals_grid[:dim - 1, :dim - 1, :]

    ''' OpenGL mesh '''
    # indices = []  # unused
    normals = []
    vertices = []

    print('Creating mesh...')
    for x in range(dim - 2):
        for y in range(dim - 2):
            # x is left to right
            # y is up
            # z is forward

            ''' Vertices '''
            v1 = np.array([x, terrain[x, y], y])
            v2 = np.array([x + 1, terrain[x + 1, y], y])
            v3 = np.array([x, terrain[x, y + 1], y + 1])
            v4 = np.array([x + 1, terrain[x + 1, y + 1], y + 1])

            vertices.extend([v1, v3, v2] + [v2, v3, v4])

            n1 = normals_grid[x, y, :]
            n2 = normals_grid[x, y + 1, :]
            n3 = normals_grid[x + 1, y, :]
            n4 = normals_grid[x + 1, y + 1, :]

            normals.extend([n1, n3, n2] + [n2, n3, n4])

            ''' Indices '''
            i1 = y * dim + x
            i2 = y * dim + x + 1
            i3 = (y + 1) * dim + x
            i4 = (y + 1) * dim + x + 1

            # the vertices look like this:
            # 1---2
            # | / |
            # 3---4

            # triangle vertices go ``counter-clockwise``
            # first triangle is top-left 1-3-2
            # second one is bottom-right 2-3-4

            # indices.extend([i1, i2, i3] + [i2, i4, i3])

            ''' Normals '''
            # how many per vertex? 1
            # n1 = np.cross(v2 - v1, v3 - v1)
            # n2 = np.cross(v4 - v2, v3 - v2)

            # y-component of the normal is 1 - but the specific value is not important, as it will get normalized
            # x-component = grad_x[x, y]
            # z-component = grad_y[x, y]

    ''' Lava '''

    vertices_lava = []
    normals_lava = []

    for x, z in crater_inside:
        # crater_inside has [x, z], crater_edge_height has [y]
        v1 = np.array([x, crater_edge_height, z])
        v2 = np.array([x + 1, crater_edge_height, z])
        v3 = np.array([x, crater_edge_height, z + 1])
        v4 = np.array([x + 1, crater_edge_height, z + 1])

        vertices_lava.extend([v1, v3, v2] + [v2, v3, v4])

        n1 = np.array([0, 1, 0])
        # normals are the same for all vertices
        normals_lava.extend([n1, n1, n1] + [n1, n1, n1])

    ''' Save all terrain data to npz '''
    vertices = np.array(vertices, dtype=np.float32)
    normals = np.array(normals, dtype=np.float32)

    vertices_lava = np.array(vertices_lava, dtype=np.float32)
    normals_lava = np.array(normals_lava, dtype=np.float32)

    save_i('assets/terrain', overwrite=True,
           ground_vertices=vertices, ground_normals=normals, ground_grid=terrain,
           lava_vertices=vertices_lava, lava_normals=normals_lava)

    print('Done')
