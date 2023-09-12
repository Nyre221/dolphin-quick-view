from PyQt5.QtWidgets import (QHBoxLayout,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget)

from PyQt5.QtCore import Qt,QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QWidget):

    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.setFocus()
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()

        #play button
        self.play_button = QPushButton()
        self.play_button.setFixedHeight(24)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.pressed.connect(self.play)

        #position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        #in order to avoid glitch the media is paused when the slider is moved 
        self.position_slider.sliderPressed.connect(lambda: self.mediaPlayer.pause())
        self.position_slider.sliderReleased.connect(self.setPosition)


        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)


        main_layout = QVBoxLayout()
        main_layout.addWidget(videoWidget)
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)


    def open(self,path):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.play()


    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState :
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))


    def positionChanged(self, position):
        self.position_slider.setValue(position)


    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)
    

    def setPosition(self):
        self.mediaPlayer.setPosition(self.position_slider.value())
        self.play()


    def hide(self) -> None:
        self.mediaPlayer.stop()
        return super().hide()
