import numpy as np
import matplotlib.pyplot as plt

def generate_terrain(crater_center = (50, 50),
                crater_radius = 30,
                crater_height = 10,
                hole_radius = 10):
    
    ground = np.zeros((100, 100), dtype=np.float32)

    # terrain surface - perlin noise
    for f in range(1, 10):
        for i in range(100):
            for j in range(100):
                ground[i, j] += np.sin(i / f) * np.sin(j / f) * f /100

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
    plt.show()

if __name__ == "__main__":
    # # plot crater
    # plt.imshow(ground, cmap='gray')
    # plt.show()
    ground = generate_terrain()
    plot_terrain(ground)



