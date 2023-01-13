import io
import tkinter as tk
from tkinter import ttk, BOTH
from tkinter import Frame, Label, Button
from urllib.request import urlopen
from nba_api.stats.endpoints import playercareerstats
import tkinter.messagebox
from PIL import Image, ImageTk
from ttkwidgets.autocomplete import AutocompleteCombobox
from nba_api.stats.static import players
import pandas as pd
pd.set_option('display.max_columns', None)


root = tkinter.Tk() #stworzenie okienka
root.title('NBA stats')
root.geometry('600x400')
root.grid_rowconfigure(0,weight=1)
root.grid_columnconfigure(0,weight=1)
playersFrame = Frame(root, bg='#ffffff')
playersFrame.grid(row=0,column=0,sticky="nsew")

teamsFrame  = Frame(root, bg='#ffffff')
teamsFrame.grid(row=0,column=0,sticky="nsew")
def create_menu():
    def createPlayers():

        imageFrame = Frame(playersFrame, bg='#ffffff')  # frame odpowiedzialny za wyświetlenie zdjęcia zawodnika
        imageFrame.place(relx=0.5, rely=0.0, width=260, height=190, anchor='n')
        imageLabel = Label(imageFrame)
        imageLabel.pack()

        searchFrame = Frame(playersFrame, bg='#ffffff')  # frame dotyczący wyszukiwania zawodnika
        searchFrame.place(relx=0.5, rely=0.5, relheight=0.1, relwidth=0.3, anchor='n')
        playersArray = pd.DataFrame(
            players.get_active_players()).full_name.values.tolist()  # pobranie listy nazwisk graczy do wyszukiwania
        searchEntry = AutocompleteCombobox(searchFrame, width=30,
                                           completevalues=playersArray)  # widget do wyboru zawodnika z autokompletacją wyszukiwania
        searchEntry.pack()

        def showPlayerStats():  # funkcja do wyświetlenia informacji o graczu
            # pobranie id gracza potrzebnego do pobrania statystyk oraz zdjęcia gracza
            player_id = pd.DataFrame(players.find_players_by_full_name(searchEntry.get())).id[0]

            photo_url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
            url = urlopen(photo_url)
            image_raw = io.BytesIO(url.read())  # pobranie zdjęcia z linku
            image_pil = Image.open(image_raw)  # konwersja zdjęcia na zmienną pillową
            image_tk = ImageTk.PhotoImage(image_pil)  # konwersja zdjęcia na kompatybilne z tkinter
            url.close()
            imageLabel.configure(image=image_tk)  # ustawienie zdjęcia w widgetcie label
            imageLabel.image = image_tk  # bez tej operacji garbage collector usuwa zdjęcie
            season_stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
            season_stats = season_stats[['SEASON_ID', 'GP', 'MIN', 'PTS', 'PF',
                                         'TOV', 'BLK', 'STL', 'AST', 'OREB', 'DREB']]
            season_stats = season_stats[season_stats.SEASON_ID == '2022-23']
            columns = season_stats.columns.tolist()
            try:
                tree.delete('id')
            except Exception:
                pass
            tree.configure(columns=columns)
            for column in columns:
                tree.column(column, minwidth=0, width=55)
                tree.heading(column, text=column)
            for index, row in season_stats.iterrows():
                id = tree.insert("", 'end', 'id', values=list(row))

        searchButton = Button(searchFrame, text="Get player data", command=showPlayerStats)
        searchButton.place(relx=0, rely=0.5, relheight=0.5, relwidth=1)

        tree = ttk.Treeview(playersFrame, show='headings')
        tree.place(relx=0, rely=0.7, relheight=0.2, relwidth=1)

        playersFrame.pack_forget()
    menubar = tk.Menu(root)
    createPlayers()

    menubar.add_command(label='Players',command=playersFrame.tkraise)
    menubar.add_command(label='Teams',command=teamsFrame.tkraise)
    root.config(menu=menubar)

create_menu()

root.mainloop()