import glob
import os
import sys
import random

import cv2
import numpy as np

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import datetime
import carla
import time
import multiprocessing

IM_WIDTH = 1280
IM_HEIGHT = 720


class setUp():
    def __init__(self, numar_vehicule=0):
        self.numar_vehicule = numar_vehicule
        self.lista_obiect = []  # se populeaza cu vehicule, senzori, obiecte
        self.stabileste_conexiunea()
        self.genereaza_mediu(numar_vehicule)

    def run(self):
        self.applyAutoPilot()

    def release(self):
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.lista_obiect])

    def stabileste_conexiunea(self):
        self.client = carla.Client("127.0.0.1", 2000)  # server, port
        self.client.set_timeout(2.0)  # Timp de asteptare pentru setarea mediului (recomandat 10s, suficient 2s)
        self.lume = self.client.load_world('Town02')  # Default este 03, optiuni intre 01 si 07
        # self.lume = self.client.get_world()

    def genereaza_mediu(self, numar_vehicule=0):
        self.lista_pozitii_spawn = self.lume.get_map().get_spawn_points()  # Aleatoriu, td -> setata prin parametru
        self.blueprint_library = self.lume.get_blueprint_library()
        tm = self.client.get_trafficmanager(2000)
        self.lume.set_weather(carla.WeatherParameters.Default)
        if numar_vehicule > 0 and numar_vehicule < len(self.lista_pozitii_spawn):
            for _ in range(numar_vehicule):
                pozitie_spawn = random.choice(
                    self.lista_pozitii_spawn)  # Se selecteaza aleator coordonatele de spawnare
                tip_vehicul = random.choice(self.blueprint_library.filter('vehicle.*'))
                self.vehicul = self.lume.spawn_actor(tip_vehicul, pozitie_spawn)
                self.lista_obiect.append(self.vehicul)  # Se adauga vehiculul creat in lista de obiecte
                self.lista_pozitii_spawn.remove(pozitie_spawn)  # Pozitia de spawn este stearsa din lista
        else:
            print("Numarul de vehicule poate genera probleme!")  # tb, raise error

    def applyAutoPilot(self):
        tm = self.client.get_trafficmanager(2000)
        tm_port = tm.get_port()
        for v in self.lista_obiect:
            v.set_autopilot(True, tm_port)

    def getBP(self):
        return self.blueprint_library

    def getLeftSpawnPositions(self):
        return self.lista_pozitii_spawn

    def getWorld(self):
        return self.lume

    def addActor(self, actor):
        self.lista_obiect.append(actor)


class MyVehicle():
    def __init__(self, venv, vehName):
        self.enviroment = venv
        self.lista_imagini_achizitionate = []
        self.setModel(vehName)
        self.attachCam()

    def setModel(self, vehName):
        self.MyCar = self.enviroment.getWorld().spawn_actor(self.enviroment.getBP().filter(vehName)[0],
                                                            random.choice(self.enviroment.getLeftSpawnPositions()))
        self.enviroment.addActor(self.MyCar)

    def attachCam(self):
        self.sensors_list = []
        self.camera = self.enviroment.getBP().find('sensor.camera.rgb')
        self.camera.set_attribute('image_size_x', f'{IM_WIDTH}')
        self.camera.set_attribute('image_size_y', f'{IM_HEIGHT}')
        self.camera.set_attribute('fov', '110')
        # self.camera.set_attribute('enable_postprocess_effects', str(False))
        self.camera.set_attribute('sensor_tick', '1.0')
        spawn_point = carla.Transform(carla.Location(x=1.8, z=2))  # FPS -> {0.5 0.4 1.2}, Central = {1.8, 2}
        self.camera_sensor = self.enviroment.getWorld().spawn_actor(self.camera, spawn_point, attach_to=self.MyCar)
        self.sensors_list.append(self.camera_sensor)
        self.camera_sensor.listen(lambda data: self.auto_replay(data))

    def process_img(self, image):
        start = datetime.datetime.now()
        imagine_matrice = np.array(image.raw_data)  # conversie imagine in array numpy (RGBA)
        imagine_modificata = imagine_matrice.reshape((IM_HEIGHT, IM_WIDTH, 4))  # redimennsionarea in RGBA
        imagine_convertita = imagine_modificata[200:480, 0:580,
                             :3]  # stergem al 4-lea element din fiecare pixel (Elementul AFLA) -> RGBA - RGB  + Rezie pentru lag fix
        cv2.imshow("", imagine_convertita)
        cv2.waitKey(1)
        print("Imaginea procesata si afisata in : " + str(datetime.datetime.now() - start))
        return imagine_convertita / 255.0  # normalizare la spectrul RGBA, de folosit in viitor

    def auto_replay(self, image):
        imagine_matrice = np.array(image.raw_data)  # conversie imagine in array numpy (RGBA)
        imagine_modificata = imagine_matrice.reshape((IM_HEIGHT, IM_WIDTH, 4))  # redimennsionarea in RGBA
        imagine_convertita = imagine_modificata[:, :,:3]  # stergem al 4-lea element din fiecare pixel (Elementul AFLA) -> RGBA - RGB  + Rezie pentru lag fix
        self.lista_imagini_achizitionate.append(imagine_convertita)

    def playback(self):
        print(len(self.lista_imagini_achizitionate))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter('video.mp4', fourcc, 1, (IM_WIDTH, IM_HEIGHT))

        for frame in self.lista_imagini_achizitionate:
            cv2.imshow("Simulation Result", frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    environment = setUp(80)
    myCar = MyVehicle(environment, "Tesla")

    environment.run()
    time.sleep(10)
    environment.release()
    myCar.playback()
