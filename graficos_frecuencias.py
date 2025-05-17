import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ruido_rosa_frec = mpimg.imread("ruidorosa_frecuencias.jpg")
plt.imshow(ruido_rosa_frec)
plt.axis("off")  # Oculta los ejes
plt.show()

sweep_frec = mpimg.imread("sweep_frecuencias.jpg")
plt.imshow(sweep_frec)
plt.axis("off")
plt.show()

filtro_inv_frec = mpimg.imread("inversesweep_frecuencias.jpg")
plt.imshow(filtro_inv_frec)
plt.axis("off")
plt.show()