import numpy as np
import matplotlib.pyplot as plt


# perlin noise code adapted from: https://github.com/pvigier/perlin-numpy
def generate_perlin_noise_2d(shape, res):
    def smoothen(t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    if shape[0] % res[0] != 0:
        d = (d[0] + 1, d[1])
    if shape[1] % res[1] != 0:
        d = (d[0], d[1] + 1)

    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)[:shape[0], :shape[1]]
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)[:shape[0], :shape[1]]
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)[:shape[0], :shape[1]]
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)[:shape[0], :shape[1]]
    # Ramps
    n00 = np.sum(grid * g00, 2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, 2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, 2)
    # Interpolation
    t = smoothen(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)


def generate_fractal_noise_2d(shape, res, octaves=1, persistence=0.5):
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        perlin = generate_perlin_noise_2d(shape, (frequency * res[0], frequency * res[1]))
        noise += amplitude * perlin
        frequency *= 2
        amplitude *= persistence
    return noise


def generate_terrain(dim=100,
                     crater_center=(50, 50),
                     crater_radius=30,
                     crater_height=100,
                     hole_radius=10,
                     noise_amplitude=50):
    ground = np.zeros((dim, dim), dtype=np.float32)

    # perlin noise
    ground += noise_amplitude * generate_fractal_noise_2d(ground.shape, res=(1, 1), octaves=4, persistence=0.4)

    # gaussian crater
    for i in range(100):
        for j in range(100):
            dist = np.sqrt((i - crater_center[0]) ** 2 + (j - crater_center[1]) ** 2)
            ground[i, j] += crater_height * np.exp(-dist / crater_radius)

    # hole in crater
    for i in range(100):
        for j in range(100):
            dist = np.sqrt((i - crater_center[0]) ** 2 + (j - crater_center[1]) ** 2)

            # gradual transition to crater hole
            # if dist < hole_radius + crater_radius / 2:
            #     ground[i, j] -= np.exp(-dist / crater_radius) * crater_height / 8
            # to be finished

            if dist < hole_radius:
                ground[i, j] = 0

    return ground


def plot_terrain(ground):
    # plot crater 3d surface
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    x = np.arange(0, 100, 1)
    y = np.arange(0, 100, 1)
    X, Y = np.meshgrid(x, y)
    ax.plot_surface(X, Y, ground, cmap='gray')
    # xyz limit 0 to 100
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    # ax.set_zlim(0, 100)

    plt.tight_layout()
    plt.show()
    plt.close(fig)


if __name__ == "__main__":
    # set manual seed - always makes the same crater
    np.random.seed(0)

    # plot crater
    ground = generate_terrain(crater_center=(60, 80), crater_height=150)
    plot_terrain(ground)

    # save crater .npy
    np.save('crater_terrain_grid.npy', ground)


