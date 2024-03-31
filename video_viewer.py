from PySide6.QtWidgets import (QHBoxLayout,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget)
from PySide6.QtGui import QShortcut
from PySide6.QtCore import Qt,QUrl
from PySide6.QtMultimedia import QMediaPlayer,QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

class VideoViewer(QWidget):

    def __init__(self, parent=None):
        super(VideoViewer, self).__init__(parent)
        self.setFocus()
        self.media_player = QMediaPlayer()
        self.videoWidget = QVideoWidget()
        self.current_file = None
        #play button
        self.play_button = QPushButton()
        self.play_button.setFixedHeight(24)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.pressed.connect(self.play)
        #audio output
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        #position slider
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        #in order to avoid glitch the media is paused when the slider is moved 
        self.position_slider.sliderPressed.connect(lambda: self.media_player.pause())
        self.position_slider.sliderReleased.connect(self.setPosition)


        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.position_slider)


        main_layout = QVBoxLayout()
        main_layout.addWidget(self.videoWidget)
        main_layout.addLayout(controls_layout)
        self.setLayout(main_layout)
        
        self.media_player.setVideoOutput(self.videoWidget)
        self.media_player.playbackStateChanged.connect(self.playbackStateChanged)
        self.media_player.positionChanged.connect(self.positionChanged)
        self.media_player.durationChanged.connect(self.durationChanged)

        self.set_shortcut()


    def open(self,path):
        self.current_file = path
        self.videoWidget.setFocus()
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.play()


    def play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        elif self.media_player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.media_player.play()
        elif self.media_player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
            self.media_player.setSource(QUrl.fromLocalFile(self.current_file))
            self.media_player.play()


    def playbackStateChanged(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.play_button.setIcon(
                    self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))


    def positionChanged(self, position):
        self.position_slider.setValue(position)


    def durationChanged(self, duration):
        self.position_slider.setRange(0, duration)
    

    def setPosition(self):
        self.media_player.setPosition(self.position_slider.value())
        self.play()



    def time_back(self):
        #milliseconds: 10 sec
        mseconds_back = 10000
        current_pos = self.media_player.position()
        if current_pos -  mseconds_back > 0:
            self.media_player.setPosition(current_pos-mseconds_back)
            if self.media_player.playbackState() ==  QMediaPlayer.PlaybackState.StoppedState:
                self.play()
        else:
            self.media_player.setPosition(0)



    def time_forward(self):
        total_time = self.media_player.duration()
        #milliseconds: 10 sec
        mseconds_forward= 10000
        current_pos = self.media_player.position()
        if mseconds_forward + current_pos < total_time:
            self.media_player.setPosition( mseconds_forward + current_pos)
        else:
            # reaches end of video.
            # -100 is used to trigger the "playbackStateChanged" signal.
            self.media_player.setPosition(total_time-100)

    def set_shortcut(self):
        QShortcut(Qt.Key.Key_Down, self).activated.connect(self.time_back)
        QShortcut(Qt.Key.Key_Up, self).activated.connect(self.time_forward)



    def hide(self) -> None:
        self.media_player.stop()
        return super().hide()
