import io
from urllib.request import urlopen

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguestandings

import tkinter as tk
from tkinter import ttk, BOTH
from tkinter import Frame, Label, Button
import tkinter.messagebox
from PIL import Image, ImageTk
from ttkwidgets.autocomplete import AutocompleteCombobox

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
pd.set_option('display.max_columns', None)


def createPlayers():
    imageFrame = Frame(playersFrame, bg='#ffffff')  # frame odpowiedzialny za wyświetlenie zdjęcia zawodnika
    imageFrame.place(relx=0.5, rely=0.0, width=260, height=190, anchor='n')
    imageLabel = Label(imageFrame)
    imageLabel.pack()

    tree = ttk.Treeview(playersFrame, show='headings')# stworzenie tabeli
    tree.place(relx=0, rely=0.7, relheight=0.2, relwidth=1)
    columns = ['SEASON_ID', 'GP', 'MIN', 'PTS', 'PF','TOV', 'BLK', 'STL', 'AST', 'OREB', 'DREB']
    tree.configure(columns=columns)
    for column in columns:
        tree.column(column, minwidth=0, width=55)
        tree.heading(column, text=column)
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
        #pobranie danych o statystykach gracza
        season_stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        season_stats = season_stats[['SEASON_ID', 'GP', 'MIN', 'PTS', 'PF',
                                     'TOV', 'BLK', 'STL', 'AST', 'OREB', 'DREB']]
        season_stats = season_stats[season_stats.SEASON_ID == '2022-23']

        try:
            tree.delete('row') # usunięcie danych z tabeli dotyczących wcześniej wyszukanego zawodnika
        except Exception:
            pass
        for index, row in season_stats.iterrows():
            id = tree.insert("", 'end', 'row', values=list(row)) #dodanie danych do tabeli

    searchFrame = Frame(playersFrame, bg='#ffffff')  # frame dotyczący wyszukiwania zawodnika
    searchFrame.place(relx=0.5, rely=0.5, relheight=0.1, relwidth=0.3, anchor='n')
    playersArray = pd.DataFrame(players.get_active_players()).full_name.values.tolist()  # pobranie listy nazwisk graczy do wyszukiwania
    searchEntry = AutocompleteCombobox(searchFrame, width=30,
                                       completevalues=playersArray)  # widget do wyboru zawodnika z autokompletacją wyszukiwania
    searchEntry.pack()
    searchButton = Button(searchFrame, text="Get player data", command=showPlayerStats)
    searchButton.place(relx=0, rely=0.5, relheight=0.5, relwidth=1)

    playersFrame.pack_forget()

def createHeatMap(side=0):
    searchFrame = Frame(heatmapFrame, bg='')  # frame dotyczący wyszukiwania zawodnika
    searchFrame.place(relx=side+0.25, rely=0.1, relheight=0.15, relwidth=0.35, anchor='n')
    playersArray = pd.DataFrame(players.get_active_players()).full_name.values.tolist()


    plotLabel = Label(heatmapFrame)
    plotLabel.place(relx=side+0.025, rely=0.3, relheight=0.6, relwidth=0.45)

    def show_shot_graph(player_id, season='2022-23'):
        for widget in plotLabel.winfo_children():  # usunięcie poprzednio wygenerowanego wykresu jeśli taki powstał
            widget.destroy()

        # pobranie i przygotowanie danych o rzutach zawodnika z wybranego sezonu
        shoot_stats = shotchartdetail.ShotChartDetail(player_id=player_id,season_nullable=season,team_id=0,context_measure_simple='FGA',
                    season_type_all_star = ['Regular Season', 'Playoffs']).get_data_frames()[0]
        if shoot_stats.empty:
            tkinter.messagebox.showerror("Niepoprawny sezon", "Brak danych dla zawodnika w podanym sezonie")
            return 0
        else:
            shoot_stats=shoot_stats[['EVENT_TYPE','LOC_X','LOC_Y']]
            shoot_stats['EVENT_TYPE']= shoot_stats['EVENT_TYPE'].apply(lambda x:0 if x=='Missed Shot' else 1)

            #stworzenie wykresu
            def draw_court(ax=None, color='black', lw=2, outer_lines=False): #funkcja zapożyczona ze strony https://notebook.community/bradleyfay/py-Goldsberry/docs/Visualizing%20NBA%20Shots%20with%20py-Goldsberry
                # If an axes object isn't provided to plot onto, just get current one
                if ax is None:
                    ax = plt.gca()

                # Create the various parts of an NBA basketball court

                # Create the basketball hoop
                # Diameter of a hoop is 18" so it has a radius of 9", which is a value
                # 7.5 in our coordinate system
                hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

                # Create backboard
                backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

                # The paint
                # Create the outer box 0f the paint, width=16ft, height=19ft
                outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                                      fill=False)
                # Create the inner box of the paint, widt=12ft, height=19ft
                inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                                      fill=False)

                # Create free throw top arc
                top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                                     linewidth=lw, color=color, fill=False)
                # Create free throw bottom arc
                bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                                        linewidth=lw, color=color, linestyle='dashed')
                # Restricted Zone, it is an arc with 4ft radius from center of the hoop
                restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                                 color=color)

                # Three point line
                # Create the side 3pt lines, they are 14ft long before they begin to arc
                corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                                           color=color)
                corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
                # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
                # I just played around with the theta values until they lined up with the
                # threes
                three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                                color=color)

                # Center Court
                center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                                       linewidth=lw, color=color)
                center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                                       linewidth=lw, color=color)

                # List of the court elements to be plotted onto the axes
                court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                                  bottom_free_throw, restricted, corner_three_a,
                                  corner_three_b, three_arc, center_outer_arc,
                                  center_inner_arc]

                if outer_lines:
                    # Draw the half court line, baseline and side out bound lines
                    outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                            color=color, fill=False)
                    court_elements.append(outer_lines)

                # Add the court elements onto the axes
                for element in court_elements:
                    ax.add_patch(element)

                return ax

            fig = plt.figure(figsize=(5,4.7))
            plt.xlim(-250, 250)
            plt.ylim(422.5, -47.5)  # limity wielkości wykresu pozwalające zachować odpowiednie proporcje boiska
            plt.hexbin(x=shoot_stats.LOC_X, y=shoot_stats.LOC_Y, C=shoot_stats.EVENT_TYPE,  extent=(-250, 250, 422.5, -47.5), gridsize=40,  cmap='Blues',edgecolors='Grey')
            draw_court(outer_lines=False, color="black") #narysowanie boiska

            cur_axes = plt.gca()
            cur_axes.axes.get_xaxis().set_visible(False)
            cur_axes.axes.get_yaxis().set_visible(False) #usunięcie niepotrzebnych osi

            plotCanvas = FigureCanvasTkAgg(fig,plotLabel) #umieszczenie wykresu w plotLabel
            plotCanvas.get_tk_widget().pack(expand=True)

    searchLabel = Label(searchFrame, text="Player")
    searchLabel.place(relx=0, rely=0, relheight=0.3, relwidth=0.3)

    searchEntry = AutocompleteCombobox(searchFrame, width=30,completevalues=playersArray)
    searchEntry.place(relx=0.3, rely=0, relheight=0.3, relwidth=0.7)

    seasonLabel = Label(searchFrame, text="Season")
    seasonLabel.place(relx=0, rely=0.3, relheight=0.3, relwidth=0.3)

    seasonEntry = AutocompleteCombobox(searchFrame, width=30,completevalues= [str(x-1)+"-"+str(x)[2:4] for x in range(2023,2000,-1)])
    seasonEntry.place(relx=0.3, rely=0.3, relheight=0.3, relwidth=0.7)

    searchButton = Button(searchFrame, text="Show shoot graph",
                command=lambda:show_shot_graph(pd.DataFrame(players.find_players_by_full_name(searchEntry.get())).id[0], seasonEntry.get()))
    searchButton.place(relx=0, rely=0.6, relheight=0.4, relwidth=1)

    heatmapFrame.pack_forget()

def createStandings():
    # stworzenie tabel
    tree_west = ttk.Treeview(standingsFrame, show='headings')
    tree_west.place(relx=0, rely=0.15, relheight=0.85, relwidth=0.5)
    tree_east = ttk.Treeview(standingsFrame, show='headings')
    tree_east.place(relx=0.5, rely=0.15, relheight=0.85, relwidth=0.5)
    columns = ['Rank','Team','Record','WinPCT','L10']
    tree_west.configure(columns=columns)
    tree_east.configure(columns=columns)
    for column in columns:
        tree_west.column(column, minwidth=0, width=20)
        tree_west.heading(column, text=column)
        tree_east.column(column, minwidth=0, width=20)
        tree_east.heading(column, text=column)
    #pobranie danych
    stands = leaguestandings.LeagueStandings(season="2022-23").get_data_frames()[0][['PlayoffRank',
                'TeamName','Conference','Division','Record','WinPCT','L10']]
    stands_west = stands[stands['Conference'] == 'West']
    stands_west.drop(columns=['Conference','Division'], inplace=True)
    stands_east = stands[stands['Conference'] == 'East']
    stands_east.drop(columns=['Conference','Division'], inplace=True)
    #dodanie danych do tabeli
    for index, row in stands_west.iterrows():
        tree_west.insert("", 'end', values=list(row))
    for index, row in stands_east.iterrows():
        tree_east.insert("", 'end', values=list(row))

def createTeams():
    pass
root = tkinter.Tk() #stworzenie okienka
root.title('NBA stats')
root.geometry('900x600')
root.grid_rowconfigure(0,weight=1)
root.grid_columnconfigure(0,weight=1)

playersFrame = Frame(root, bg='#ffffff')
playersFrame.grid(row=0,column=0,sticky="nsew")

teamsFrame = Frame(root, bg='#ffffff')
teamsFrame.grid(row=0,column=0,sticky="nsew")

heatmapFrame = Frame(root, bg='#ffffff')
heatmapFrame.grid(row=0,column=0,sticky="nsew")

standingsFrame = Frame(root,bg='#ffffff')
standingsFrame.grid(row=0,column=0,sticky="nsew")

def create_menu():

    menubar = tk.Menu(root)
    createPlayers()
    createHeatMap()
    createHeatMap(0.5)
    createTeams()
    createStandings()
    menubar.add_command(label='Players',command=playersFrame.tkraise)
    menubar.add_command(label='Teams',command=teamsFrame.tkraise)
    menubar.add_command(label='Shot heatmap',command=heatmapFrame.tkraise)
    menubar.add_command(label='Standings',command=standingsFrame.tkraise)
    root.config(menu=menubar)

create_menu()

root.mainloop()