import glob
import os
import sys
import random
import psutil
import cv2
import datetime
import numpy as np
from multiprocessing import Process

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import time
carla_path = "D:\CARLA_0.9.10"

IM_WIDTH = 1080
IM_HEIGHT = 720

class SetUp:
    def __init__(self, townName='', numar_vehicule=0, numar_pietoni=0):
        self.numar_vehicule = numar_vehicule
        self.numar_pietoni = numar_pietoni
        self.lista_vehicule = []
        self.lista_senzori = []
        self.lista_pietoni = []
        self.stabileste_conexiunea(townName)
        self.genereaza_mediu(numar_vehicule)
        self.adaugaPietoni(numar_pietoni)

    def run(self, pv_execution_time):
        self.execution_time = pv_execution_time
        self.applyAutoPilot()
        time.sleep(self.execution_time)

    # @todo index out of range error
    def stop(self):
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.lista_vehicule])
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.lista_senzori])
        try:
            for i in range(0, len(self.all_id), 2):
                self.all_actors[i].stop()
        except IndexError:
            pass
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.all_id])

    def stabileste_conexiunea(self, townName):
        self.client = carla.Client("127.0.0.1", 2000)  # server, port
        available_maps = [city.split('/')[4] for city in self.client.get_available_maps()]
        self.town_name = townName if townName in available_maps else "Town01"
        self.lume = self.client.load_world(
            self.town_name)  # Default este 03, optiuni intre 01 si 07 Town10HD, # Town07 contine semne de Stop si Yield
        self.client.set_timeout(2.0) if self.town_name != "Town10HD" else self.client.set_timeout(5.0)  # Timp de asteptare pentru setarea mediului (recomandat 10s, suficient 2s)

    def genereaza_mediu(self, numar_vehicule=0):
        self.lista_pozitii_spawn = self.lume.get_map().get_spawn_points()  # Aleatoriu, td -> setata prin parametru
        self.blueprint_library = self.lume.get_blueprint_library()
        self.lume.set_weather(carla.WeatherParameters.Default)
        if 0 < numar_vehicule < len(self.lista_pozitii_spawn):
            for _ in range(numar_vehicule):
                pozitie_spawn = random.choice(
                    self.lista_pozitii_spawn)  # Se selecteaza aleator coordonatele de spawnare
                tip_vehicul = random.choice(self.blueprint_library.filter('vehicle.*'))
                self.vehicul = self.lume.spawn_actor(tip_vehicul, pozitie_spawn)
                self.lista_vehicule.append(self.vehicul)  # Se adauga vehiculul creat in lista de obiecte
                self.lista_pozitii_spawn.remove(pozitie_spawn)  # Pozitia de spawn este stearsa din lista
        else:
            print("Numarul de vehicule poate genera probleme!")  # tb, raise error

    def adaugaPietoni(self, numar_pietoni):
        self.lista_pozitii_spawn_pietoni = []
        blueprintsWalkers = self.lume.get_blueprint_library().filter("walker.pedestrian.*")
        walkers_list = []
        self.all_id = []
        for _ in range(numar_pietoni):
            spawn_point = carla.Transform()
            spawn_point.location = self.lume.get_random_location_from_navigation()
            spawn_point.location.z += 1
            if spawn_point is not None and spawn_point not in self.lista_pozitii_spawn_pietoni:
                self.lista_pozitii_spawn_pietoni.append(spawn_point)

        batch = []
        for spawn_point in self.lista_pozitii_spawn_pietoni:
            walker_bp = random.choice(blueprintsWalkers)
            batch.append(carla.command.SpawnActor(walker_bp, spawn_point))

        # apply the batch
        results = self.client.apply_batch_sync(batch, True)
        for index in range(len(results)):
            walkers_list.append({"id": results[index].actor_id})

        batch = []
        walker_controller_bp = self.lume.get_blueprint_library().find('controller.ai.walker')
        for index in range(len(walkers_list)):
            batch.append(carla.command.SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[index]["id"]))

        results = self.client.apply_batch_sync(batch, True)
        for index in range(len(results)):
            walkers_list[index]["con"] = results[index].actor_id

        for index in range(len(walkers_list)):
            self.all_id.append(walkers_list[index]["con"])
            self.all_id.append(walkers_list[index]["id"])
            self.all_actors = self.lume.get_actors(self.all_id)

        for index in range(0, len(self.all_actors), 2):
            self.all_actors[index].start()  # porneste controller
            self.all_actors[index].go_to_location(
                self.lume.get_random_location_from_navigation())  # se deplaseaza la o pozitie aleatorie
            self.all_actors[index].set_max_speed(1 + random.random())  # cu o viteza aleatorie

    def applyAutoPilot(self):
        tm = self.client.get_trafficmanager(2000)
        tm_port = tm.get_port()
        for vehicul in self.lista_vehicule:
            vehicul.set_autopilot(True, tm_port)

    # @todo bug fix -> ramane agatata pe undeva ? :))
    def startCARLA(self):
        try:
            os.chdir(carla_path)
            if not ("CarlaUE4.exe" in (process.name() for process in psutil.process_iter())):
                os.system("CarlaUE4.exe --windowed --resX=1280 --resY=720")
            else:
                print("E deja pornit!")

        except FileNotFoundError:
            print("Nu s-a gasit directorul " + str(carla_path))
        finally:
            pass
        time.sleep(5)

    def getBP(self):
        return self.blueprint_library

    def getLeftSpawnPositions(self):
        return self.lista_pozitii_spawn

    def getWorld(self):
        return self.lume

    def addActor(self, actor):
        self.lista_vehicule.append(actor)

    def addSensor(self, sensor):
        self.lista_senzori.append(sensor)


class MyVehicle:
    def __init__(self, venv, vehName):
        self.enviroment = venv
        self.lista_imagini_achizitionate = []
        self.lista_imagini_ss_achizitionate = []
        self.setModel(vehName)
        RGBCam = Process(target=self.attachRGBCam())
        SSCam = Process(target=self.attachSSCam())
        RGBCam.start();
        SSCam.start()
        RGBCam.join();
        SSCam.join()

    def setModel(self, vehName):
        self.MyCar = self.enviroment.getWorld().spawn_actor(self.enviroment.getBP().filter(vehName)[0],
                                                            random.choice(self.enviroment.getLeftSpawnPositions()))
        self.enviroment.addActor(self.MyCar)

    def attachRGBCam(self):
        self.camera_RGB = self.enviroment.getBP().find('sensor.camera.rgb')
        self.camera_RGB.set_attribute('image_size_x', f'{IM_WIDTH}')
        self.camera_RGB.set_attribute('image_size_y', f'{IM_HEIGHT}')
        self.camera_RGB.set_attribute('fov', '90')
        self.camera_RGB.set_attribute('sensor_tick', '0.0')
        spawn_point_RGB = carla.Transform(carla.Location(x=2, z= 1.2))  # FOV 110: 3RD {x=-5, z=2} Central {x=1, z=1.2}, FPS{x=.5, y=-.4, z=1.1}
        self.camera_sensor_RGB = self.enviroment.getWorld().spawn_actor(self.camera_RGB, spawn_point_RGB, attach_to=self.MyCar)
        self.enviroment.addSensor(self.camera_sensor_RGB)
        self.camera_sensor_RGB.listen(lambda data: self.save_replay(data))

    def attachSSCam(self):
        self.camera = self.enviroment.getBP().find('sensor.camera.semantic_segmentation')
        self.camera.set_attribute('image_size_x', f'{IM_WIDTH}')
        self.camera.set_attribute('image_size_y', f'{IM_HEIGHT}')
        self.camera.set_attribute('fov', '100')
        self.camera.set_attribute('sensor_tick', '0.0')
        spawn_point = carla.Transform(carla.Location(x=2, z=1.2))
        self.camera_sensor = self.enviroment.getWorld().spawn_actor(self.camera, spawn_point, attach_to=self.MyCar)
        self.enviroment.addSensor(self.camera_sensor)
        #self.camera_sensor.listen(lambda image: image.save_to_disk('output/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette))
        self.camera_sensor.listen(lambda image: self.process_ss_img(image))

    def process_ss_img(self, image):
        self.lista_imagini_ss_achizitionate.append(image)

    def process_img(self, image):
        imagine_matrice = np.array(image.raw_data)  # conversie imagine in array numpy (RGBA)
        imagine_modificata = imagine_matrice.reshape((IM_HEIGHT, IM_WIDTH, 4))  # redimennsionarea in RGBA
        imagine_convertita = imagine_modificata[0:480, 0:580, :3]  # stergem al 4-lea element din fiecare pixel (Elementul AFLA) -> RGBA - RGB
        cv2.imshow("", imagine_convertita)
        cv2.waitKey(1)
        return imagine_convertita / 255.0  # normalizare la spectrul RGBA, de folosit in viitor


    def save_replay(self, image):
        imagine_matrice = np.array(image.raw_data)  # conversie imagine in array numpy (RGBA)
        imagine_modificata = imagine_matrice.reshape((IM_HEIGHT, IM_WIDTH, 4))  # redimennsionarea in RGBA
        imagine_convertita = imagine_modificata[:, :,:3]  # stergem al 4-lea element din fiecare pixel (Elementul AFLA) -> RGBA - RGB
        self.lista_imagini_achizitionate.append(imagine_convertita)

    def playbackRGB(self, action="save_file"):
        video_RGB = cv2.VideoWriter('VideoOutput.avi', cv2.VideoWriter_fourcc(*'MJPG'), int(len(self.lista_imagini_achizitionate) / environment.execution_time), (IM_WIDTH, IM_HEIGHT))
        if action == "replay":
            for frame in self.lista_imagini_achizitionate:
                cv2.imshow("Simulation video", frame)
                cv2.waitKey(1)  # 16 ms => 1000 / 16 => 60 fps
            cv2.destroyAllWindows()
        else:
            for frame in self.lista_imagini_achizitionate:
                video_RGB.write(frame)
            video_RGB.release()

    def playbackSS(self):
        for image in self.lista_imagini_ss_achizitionate:
            image.save_to_disk('output/%06d.png' % image.frame, carla.ColorConverter.CityScapesPalette)

        video = cv2.VideoWriter('SemanticVideoOutput.avi', cv2.VideoWriter_fourcc(*'MJPG'), int(len(self.lista_imagini_ss_achizitionate) / environment.execution_time), (IM_WIDTH, IM_HEIGHT))
        for img in glob.glob("output/*.png"):
            frame = cv2.imread(img)
            video.write(frame)
        video.release()

if __name__ == "__main__":
    now = datetime.datetime.now()
    environment = SetUp("Town07", 100, 50)
    myCar = MyVehicle(environment, "model3")

    environment.run(180)
    environment.stop()

    myCar.playbackRGB("save")
    myCar.playbackSS()

    print("Execuion time {}".format(datetime.datetime.now() - now))