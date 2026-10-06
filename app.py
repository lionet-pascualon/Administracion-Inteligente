import sys

import math

import random

import numpy as np

from PyQt6.QtWidgets import QApplication, QWidget

from PyQt6.QtCore import Qt, QTimer, QPointF

from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPolygonF



# Declaración segura a nivel global

MICROFONO_REAL = False

sd = None



try:

    import sounddevice as sd

    MICROFONO_REAL = True

except Exception:

    MICROFONO_REAL = False



class AtomoVozReal(QWidget):

    def __init__(self):

        super().__init__()

        self.initUI()

        self.angulo = 0.0

        self.nivel_voz = 1.0  

        self.volumen_crudo = 0.0

        self.stream = None



        # Campo de partículas de niebla amplio

        self.particulas = []

        for _ in range(70):

            self.particulas.append({

                'angulo': random.uniform(0, 2 * math.pi),

                'radio': random.uniform(90, 230),

                'velocidad': random.uniform(0.005, 0.015),

                'tamano': random.uniform(2, 5),

                'opacidad': random.randint(100, 230)

            })



        global MICROFONO_REAL

        if MICROFONO_REAL:

            try:

                self.stream = sd.InputStream(

                    channels=1, 

                    samplerate=22050, 

                    callback=self.audio_callback,

                    blocksize=512

                )

                self.stream.start()

            except Exception as e:

                print(f"No se pudo iniciar el micro: {e}")

                MICROFONO_REAL = False



        self.timer = QTimer(self)

        self.timer.timeout.connect(self.actualizar_animacion)

        self.timer.start(30)



    def audio_callback(self, indata, frames, time, status):

        try:

            volumen = np.linalg.norm(indata) * 10.0

            self.volumen_crudo = min(volumen, 2.5) # Limitado para mantener elegancia

        except Exception:

            self.volumen_crudo = 0.0



    def initUI(self):

        # Ventana más grande (650x650) para que las órbitas jamás se corten al expandirse

        self.setWindowFlags(

            Qt.WindowType.FramelessWindowHint | 

            Qt.WindowType.WindowStaysOnTopHint | 

            Qt.WindowType.Tool

        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(400, 400)



    def actualizar_animacion(self):

        global MICROFONO_REAL

        if MICROFONO_REAL:

            target = 1.0 + (self.volumen_crudo * 0.5) # Escala controlada y profesional

            self.nivel_voz += (target - self.nivel_voz) * 0.3

        else:

            self.nivel_voz = 1.0 + 0.15 * abs(math.sin(self.angulo * 2.5))



        self.angulo = (self.angulo + 0.012) % (2 * math.pi)

        for p in self.particulas:

            p['angulo'] += p['velocidad'] * self.nivel_voz



        self.update() 



    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)



        # Centro recalculado para el nuevo tamaño de 650x650

        cx, cy = 325, 325



        # ANILLOS DE ÓRBITA TRIDIMENSIONAL

        def dibujar_anillo_niebla(inclinacion_eje, desfase_rot):

            puntos = []

            rx = 210 * self.nivel_voz

            ry = (85 * self.nivel_voz)

            pasos = 100



            for i in range(pasos + 1):

                t = (i / pasos) * (2 * math.pi)

                x_base = rx * math.cos(t)

                y_base = ry * math.sin(t)



                rot = self.angulo + desfase_rot

                cos_r = math.cos(rot)

                sin_r = math.sin(rot)



                x_3d = x_base * cos_r - y_base * sin_r * math.sin(inclinacion_eje)

                y_3d = x_base * sin_r * math.cos(inclinacion_eje) + y_base * cos_r

                z_3d = x_base * sin_r * math.sin(inclinacion_eje)



                factor = 1.0 + (z_3d / 500.0)

                px = cx + x_3d * factor

                py = cy + y_3d * factor

                puntos.append(QPointF(px, py))



            brillo_rojo = int(min(60 + (self.nivel_voz * 80), 255))

            pen = QPen(QColor(255, brillo_rojo, 0, 180), 5)

            painter.setPen(pen)

            painter.setBrush(Qt.BrushStyle.NoBrush)

            painter.drawPolyline(QPolygonF(puntos))



        dibujar_anillo_niebla(inclinacion_eje=0.5, desfase_rot=0.0)

        dibujar_anillo_niebla(inclinacion_eje=1.3, desfase_rot=2.1)

        dibujar_anillo_niebla(inclinacion_eje=2.0, desfase_rot=4.2)



        # PARTÍCULAS FLOTANTES DE NIEBLA ROJA

        for p in self.particulas:

            radio_actual = p['radio'] * self.nivel_voz

            px = cx + math.cos(p['angulo']) * radio_actual

            py = cy + math.sin(p['angulo']) * (radio_actual * 0.45)



            painter.setPen(Qt.PenStyle.NoPen)

            painter.setBrush(QColor(255, 60, 20, p['opacidad']))

            painter.drawEllipse(int(px), int(py), int(p['tamano'] * self.nivel_voz), int(p['tamano'] * self.nivel_voz))



        # NÚCLEO CENTRAL

        radio_nucleo = int(75 * self.nivel_voz)

        gradiente_nucleo = QRadialGradient(cx, cy, radio_nucleo)

        gradiente_nucleo.setColorAt(0.0, QColor(255, 200, 200, 250)) 

        gradiente_nucleo.setColorAt(0.4, QColor(240, 30, 10, 230))   

        gradiente_nucleo.setColorAt(0.8, QColor(140, 0, 0, 210))     

        gradiente_nucleo.setColorAt(1.0, QColor(60, 0, 0, 240))      



        painter.setPen(QPen(QColor(255, 120, 120, 255), 3))

        painter.setBrush(gradiente_nucleo)

        painter.drawEllipse(cx - radio_nucleo, cy - radio_nucleo, radio_nucleo * 2, radio_nucleo * 2)



    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self.oldPos = event.globalPosition().toPoint()



    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.MouseButton.LeftButton:

            delta = event.globalPosition().toPoint() - self.oldPos

            self.move(self.pos() + delta)

            self.oldPos = event.globalPosition().toPoint()



    def closeEvent(self, event):

        global MICROFONO_REAL

        if MICROFONO_REAL and hasattr(self, 'stream') and self.stream:

            try:

                self.stream.stop()

                self.stream.close()

            except Exception:

                pass

        event.accept()



if __name__ == '__main__':

    app = QApplication(sys.argv)

    atomo = AtomoVozReal()

    atomo.show()

    sys.exit(app.exec()) 

