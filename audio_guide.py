# import external libraries
import vlc
# import standard libraries
import sys
import tkinter as Tk
from tkinter import ttk
from tkinter.messagebox import showerror
from os import path
from os.path import expanduser
import time
from PIL import ImageTk, Image


#_isWindows = sys.platform.startswith('win')


class Player(Tk.Frame):
    """The main window has to deal with events.
    """
    _geometry = ''
    _stopped  = None

    def __init__(self, parent, title=None, video=''):
        Tk.Frame.__init__(self, parent)

        self.parent = parent  # == root
        self.parent.iconbitmap("media/audio_icone.ico")
        self.parent.title("Audio-Guide on Shepard Fairey")
        self.video = expanduser(video)
        self.Menu()

    def Room_1(self):
        self.suppr()
        self.video += "Room_1.mp3"
        self.AudioDisplay()

    def Room_2(self):
        self.suppr()
        self.video += "Room_2.mp3"
        self.AudioDisplay()

    def Room_3(self):
        self.suppr()
        self.video += "Room_3.mp3"
        self.AudioDisplay()

    def Room_4(self):
        self.suppr()
        self.video += "Room_4.mp3"
        self.AudioDisplay()

    def Room_5(self):
        self.suppr()
        self.video += "Room_5.mp3"
        self.AudioDisplay()

    def Credits(self):
        self.suppr()
        img = ImageTk.PhotoImage(Image.open("media/credits.png"))
        credit = Tk.Label(self.parent, image = img)
        credit.image = img
        credit.pack()

        Tk.Button(self.parent, width=10, text="Back to Menu", command=self.Menu).pack(side=Tk.LEFT)
        Tk.Button(self.parent, width=10, text="Quit", command=self.parent.destroy).pack(side=Tk.RIGHT)

        self.parent.minsize(width=250, height=327)
        self.parent.maxsize(width=250, height=327)

    def suppr(self):
        for element in self.parent.winfo_children():
            element.destroy()

    def Menu(self):
        self.suppr()

        self.video = "media/"

        Tk.Button(self.parent, width=24, height=4, text="Shepard Fairey? Who is he?", command = self.Room_1).grid(row=0, column=0)
        Tk.Button(self.parent, width=24, height=4, text="From shadow to light : \n politics as a launch way", command = self.Room_2).grid(row=0, column=1)
        Tk.Button(self.parent, width=24, height=4, text="Communication by emotion : \n the power of art", command = self.Room_3).grid(row=1, column=0)
        Tk.Button(self.parent, width=24, height=4, text="The business man behind \n the scene: OBEY", command = self.Room_4).grid(row=1, column=1)
        Tk.Button(self.parent, width=24, height=4, text="New messages : news revisited", command = self.Room_5).grid(row=2, column=0)
        Tk.Button(self.parent, width=24, height=4, text="Credits", command = self.Credits).grid(row=2, column=1)

        self.parent.geometry("356x213")
        self.parent.maxsize(width=356, height=213)
        self.parent.minsize(width=356, height=213)

    def AudioDisplay(self):
        # video button

        buttons = ttk.Frame(self.parent)
        self.playButton = ttk.Button(buttons, text="Play", command=self.OnPlay)
        stop            = ttk.Button(buttons, text="Stop", command=self.OnStop)
        self.playButton.pack(side=Tk.LEFT)
        stop.pack(side=Tk.LEFT)

        # video volume slider
        self.volVar = Tk.IntVar()
        self.volSlider = Tk.Scale(buttons, variable=self.volVar, command=self.OnVolume,
                                  from_=0, to=100, orient=Tk.HORIZONTAL, length=200,
                                  showvalue=0, label='Volume')
        self.volSlider.pack(side=Tk.RIGHT)
        buttons.pack(side=Tk.BOTTOM, fill=Tk.X)


        # panel to hold player time slider
        timers = ttk.Frame(self.parent)
        self.timeVar = Tk.DoubleVar()
        self.timeSliderLast = 0
        self.timeSlider = Tk.Scale(timers, variable=self.timeVar, command=self.OnTime,
                                   from_=0, to=1000, orient=Tk.HORIZONTAL, length=500,
                                   showvalue=0)  # label='Time',
        self.timeSlider.pack(side=Tk.TOP, fill=Tk.X, expand=1)
        self.timeSliderUpdate = time.time()
        timers.pack(side=Tk.TOP, fill=Tk.X)


        # VLC player
        args = []
        self.Instance = vlc.Instance(args)
        self.player = self.Instance.media_player_new()

        #self.parent.bind("<Configure>", self.OnConfigure)  # catch window resize, etc.
        self.parent.update()

        # Estetic, to keep our video panel at least as wide as our buttons panel.
        self.parent.geometry("502x70")
        self.parent.minsize(width=502, height=70)
        self.parent.maxsize(width=502, height=70)

        self.OnPlay()
        self.OnTick()  # set the timer up

    def _Pause_Play(self, playing):
        p = 'Pause' if playing else 'Play'
        c = self.OnPlay if playing is None else self.OnPause
        self.playButton.config(text=p, command=c)
        self._stopped = False

    def _Play(self, video):
        m = self.Instance.media_new(str(video))  # Path, unicode
        self.player.set_media(m)

        self.OnPlay()

    def OnPause(self, *unused):
        """Toggle between Pause and Play.
        """
        if self.player.get_media():
            self._Pause_Play(not self.player.is_playing())
            self.player.pause()  # toggles

    def OnPlay(self, *unused):
        """Play audio
        """
        if not self.player.get_media():
            self._Play(self.video)
            self.video = ''
        elif self.player.play():  # == -1
            self.showError("Unable to play the video.")
        else:
            self._Pause_Play(True)
            vol = self.player.audio_get_volume()
            if vol > 0:
                self.volVar.set(vol)
                self.volSlider.set(vol)

    def OnStop(self, *unused):
        """Stop the player, resets media.
        """
        self.player.stop()
        self._Pause_Play(None)
        self.timeSlider.set(0)
        self._stopped = True
        self.suppr()
        self.Menu()

    def OnTick(self):
        """Timer tick, update the time slider to the video time.
        """
        if self.player:
            t = self.player.get_length() * 1e-3  # to seconds
            if t > 0:
                self.timeSlider.config(to=t)

                t = self.player.get_time() * 1e-3  # to seconds
                if t > 0 and time.time() > (self.timeSliderUpdate + 2):
                    self.timeSlider.set(t)
                    self.timeSliderLast = int(self.timeVar.get())
        self.parent.after(1000, self.OnTick)

    def OnTime(self, *unused):
        if self.player:
            t = self.timeVar.get()
            if self.timeSliderLast != int(t):
                self.player.set_time(int(t * 1e3))  # milliseconds
                self.timeSliderUpdate = time.time()

    def OnVolume(self, *unused):
        """Volume slider changed, adjust the audio volume.
        """
        vol = min(self.volVar.get(), 100)
        self.volSlider.config(label="Volume " + str(vol))
        if self.player and not self._stopped:
                self.showError("Failed to set the volume: %s." % (v_M,))

    def showError(self, message):
        """Display a simple error dialog.
        """
        self.OnStop()
        showerror(self.parent.title(), message)


root = Tk.Tk()
player = Player(root, video="")
root.mainloop()