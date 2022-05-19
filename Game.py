
#----------------------------------------- Imports-----------------------------------------------------------

import  tkinter as tk
from PIL import ImageTk, Image

from tkinter import messagebox
from tkinter.filedialog import asksaveasfile, askopenfilename


__author__ = "(F Hov)"


#------------------------------------- Parameters------------------------------------------------------------

GAME_LEVELS = {"game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

TASK_ONE=1
TASK_TWO=2

DIRECTIONS = {
    "W": (-1, 0),
    "S": (1, 0),
    "D": (0, 1),
    "A": (0, -1)}


#------------------------------------- Game Logic ------------------------------------------

#Only main difference is that for each entity or item, the colour and the name for the game was added
#Other difference the name of the dungeon was changed to game2.txt for default, as game1 and game3 not required



def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        file_contents = file.readlines()

    for i in range(len(file_contents)):
        line = file_contents[i].strip()
        row = []
        for j in range(len(file_contents)):
            row.append(line[j])
        dungeon_layout.append(row)
    
    return dungeon_layout


class Entity:
    """ """
    
    _id = "Entity"
    
    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """ """
        return self._id

    def set_collide(self, collidable):
        """ """
        self._collidable = collidable

    def can_collide(self):
        """ """
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """ """

    _id = WALL
    
    def __init__(self):
        """ """
        super().__init__()
        self.set_collide(False)
        self._name=''
        self._fill='grey'


class Item(Entity):
    """ """
    def on_hit(self, game):
        """ """
        raise NotImplementedError


class Key(Item):
    """ """

    _id = KEY

    def __init__(self):
        super().__init__() 
        self._name='Trash'
        self._fill='yellow'
    
    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())

        
        
class MoveIncrease(Item):
    """ """

    _id = MOVE_INCREASE
    

    def __init__(self, moves=5):
        """ """
        super().__init__()
        self._moves = moves
        self._name='Banana'
        self._fill='orange'

    def on_hit(self, game):
        """ """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """ """
    _id = DOOR

    def __init__(self):
        super().__init__()
        self._name='Nest'
        self._fill='Red'

    def on_hit(self, game):
        """ """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                return


class Player(Entity):
    """ """

    _id = PLAYER
   

    def __init__(self, move_count):
        """ """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None

    def set_position(self, position):
        """ """
        self._position = position

    def get_position(self):
        """ """
        return self._position

    def change_move_count(self, number):
        """
        Parameters:
            number (int): number to be added to move count
        """
        self._move_count += number

    def moves_remaining(self):
        """ """
        return self._move_count

    def add_item(self, item):
        """Adds item (Item) to inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """ """
        return self._inventory


class GameLogic(object):
    """ """
    def __init__(self, dungeon_name):
        """ """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False
        
    def get_positions(self, entity):
        """ """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """ """
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """ """
        return self._player

    def get_entity(self, position):
        """ """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """ """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """ """
        return self._game_information

    def get_dungeon_size(self):
        """ """
        return self._dungeon_size

    def move_player(self, direction):
        """ """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """ """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """ """
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """ """
        self._win = win

    def won(self):
        """ """
        return self._win




#------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------- GameApp ----------------------------------------------------

class GameApp(object):
    """Game App is a class containing the gamelogic, the command and the view"""
    
    def __init__(self, master, dungeon_name, task=TASK_ONE):
        """Initialising the Game app class"""
        
        self._master = master 
        master.title('Key Cave Adventure Game') #Title for the GUI
        self._dungeon_name = dungeon_name 
        
        self._task = task #Defining the task, either 1 or 2
        self._game= GameLogic(self._dungeon_name) #Initializing the GameLogic
        self._player = self._game.get_player() #Initializing the Player Class in the GameLogic
        

            
        self._view = View(self._master, self) #Initializing the View class, which contains the class of the KeyPad and DungeonMap

        
        self._view._keypad.bind("<Button-1>", self.button_pressed) #If the user uses left click, the button_pressed command will be used

        self._view._keypad.bind_all("w",self.key_pressed) #If the user clicks on w, the command key_pressed will be used
        self._view._keypad.bind_all("a",self.key_pressed) #If the user clicks on a, the command key_pressed will be used
        self._view._keypad.bind_all("d",self.key_pressed) #If the user clicks on d, the command key_pressed will be used
        self._view._keypad.bind_all("s",self.key_pressed) #If the user clicks on s, the command key_pressed will be used
        

        if task == TASK_TWO: #Create filemenu in the menu bar
            
            menubar = tk.Menu(self._master)
            self._master.config(menu=menubar)
        #---------------------------Save_Open menubar
            save_open = tk.Menu(menubar)
            menubar.add_cascade(label="Save/Load Game", menu=save_open)
            save_open.add_command(label="Save Game", command=self.save_game) #if pressed, definition save_game will be used
            save_open.add_command(label="Load Game",command=self.open_game) #if pressed, definition open_game will be used

        #---------------------------New_Quit Menubar
            new_quit = tk.Menu(menubar)
            menubar.add_cascade(label='New\Quit Game', menu=new_quit)
            new_quit.add_command(label="New Game",command=self.new_game) #if pressed, definition new_game will be used
            new_quit.add_command(label="Quit Game",command=self.end_game) #if pressed, definition end_game will be used


    def button_pressed(self,pixel):
        """If the user uses left click, then button pressed will be used"""
        
        tag = self._view._keypad.gettags(self._view._keypad.find_closest(pixel.x, pixel.y)) #Uses the gettag method, as tags were defined for each command on
                                                                                                #the keypad
        
        if len(tag) == 2: #if the user click within the rectangle of a command of the keypad, two tags will be given, e.g('N','Current'). Therefore any valid
                                    #command will have two tags, else the command is invald
            self._cmd = tag[0] #The command we are interested in is the first tag
            
            self.play(self._cmd) 


    def key_pressed(self,pixel):
        """ If a key is pressed, the character of the key will be retrieved and will be change to upper cases"""
        
        self._cmd = pixel.char.upper()
        
        self.play(self._cmd)
                                          
                          

    def yes_or_no(self,ans): 
        """ Def deals with answer from the messagebox
            Input(str) = yes or no"""
        
        if ans == 'yes':
            
            self.new_game()
                    

        elif ans == 'no':
            
            self.end_game()
            

    def end_game(self):
        "Used to ask the user one last time if he wants to quit the agame"""
        
        ans = messagebox.askquestion("Are you sure?","Are you sure you don't want to save the bird ?")
                                    
        if ans =='yes':
            
            self._master.destroy()
    

    def new_game(self):
        """ Def used to reset the game"""
        
        self._game = GameLogic(self._dungeon_name) #Reset the GameLogic to initial Game Logic
        self._player =self._game.get_player() #Reset the Player Class to initial Player Class
        
        self._view._dungeon_map.draw_grid(self._game.get_game_information(), self._game.get_player().get_position()) #Draw the dungeon grid
                
        self._view._status._lab_move_number.config(text ='{} moves remaining'.format(self._player.moves_remaining())) #Reset the number of moves for the status bar
        
        self._view._status._second = 0
        self._view._status._minutes = 0
        self._view._status._lab_timer.config(text='{} m {}s'.format(self._view._status._minutes,self._view._status._second)) #Reset the seconds/minutes for the status bar
        
    def save_game(self):
        """ Save files in a txt file
            Save the game information, position of player, moves remaining, seconds and minutes"""
        
        file=asksaveasfile(mode='w',defaultextension='.txt', filetypes= [('Dungeon','.txt')]) #Command use to prompt the user for the location to save the file

        dungeon = "" #initialise the dungeon representation like in A2
        player_pos = self._game.get_player().get_position() #player position
        for i in range(self._game._dungeon_size):
            rows = ""
            for j in range(self._game._dungeon_size):
                position = (i, j)
                entity = self._game._game_information.get(position)

                if entity is not None:
                    char = entity.get_id()
                elif position == player_pos:
                    char = PLAYER
                else:
                    char = SPACE
                rows += char
            if i < self._game._dungeon_size - 1:
                rows += "\n"
            dungeon += rows
        dungeon += '\n'
        
        file.write('{} \n'.format(self._dungeon_name)) #1st line dungeon name
        file.write('{} \n'.format(self._game._dungeon_size)) #2nd line dungeon size
        file.write('{} \n'.format(self._player.moves_remaining())) #3rd line player moves remaining
        file.write('{} \n'.format(self._player.get_inventory()))
        file.write('{} \n'.format(self._view._status._second)) #4th seconds
        file.write('{} \n'.format(self._view._status._minutes)) #5th minutes
        file.write(dungeon) #dungeon representation like A2

        file.close() #close the file
        
    def open_game(self):
        """Open the game, if the file is not correct an messagox error will come up"""
        try:
            filename = askopenfilename()   #open file

 
            dungeon_dic ={} #initialise the dungeon dic
            
            with open(filename, 'r') as file:
                file_contents = file.readlines()
  
            self._dungeon_name = file_contents[0].strip() #dungeon_name
            dungeon_size = int(file_contents[1].strip()) #dungeon size
            self._player._move_count = int(file_contents[2].strip()) #moves left
            player_inventory = file_contents[3].strip()
            self._view._status._second = int(file_contents[4].strip()) #seconds
            self._view._status._minutes = int(file_contents[5].strip()) #minutes

            for i in range(6,dungeon_size+6): #creating the dictionary and the player pos
                line = file_contents[i].strip()
                for j in range(0,dungeon_size):
                    row = i - 6
                    col = j
                    char = line[j]
                    if char == 'K':
                        dungeon_dic[row,col]=Key()
                    elif char == 'D':
                        dungeon_dic[row,col]=Door()
                    elif char == '#':
                        dungeon_dic[row,col]=Wall()
                    elif char == 'M':
                        dungeon_dic[row,col]=MoveIncrease()
                    elif char == 'O':
                        player_pos = (row,col)
        except:
            messagebox.showerror('Wrong File', 'choose another file')
            return

        
        self._game._game_information = dungeon_dic #updating the game info
        self._player.set_position(player_pos) #updating player position
        if player_inventory :
            self._player.add_item(Key()) #updating the inventory
        
        self._view._status._lab_move_number.config(text ='{} moves remaining'.format(self._player.moves_remaining())) #change moves remaining
        self._view._status._lab_timer.config(text='{} m {}s'.format(self._view._status._minutes,self._view._status._second)) #change minutes and seconds
        
        self._view._dungeon_map.draw_grid(self._game._game_information,player_pos) #redraw the map
        
        
    def play(self, cmd):
        """ The play definition, takes as an input a valid command and is used to play the game"""

        self._player.change_move_count(-1) #If the player enters a valid command, the move count will reduce by 1

    
        if self._task == TASK_TWO: #If task two, the status bar will be showed
            
            self._view._status._lab_move_number.config(text ='{} moves remaining'.format(self._player.moves_remaining()))
            
        
        if not self._game.collision_check(cmd): #True if the user can move toward the direction  given
            
            self._game.move_player(cmd) #Move the player
            
            self._view._dungeon_map.delete(tk.ALL) #Delete everything in the map, to update the map
            
            entity = self._game.get_entity(self._game.get_player().get_position()) #get entity
            
            if entity is not None:
                
                entity.on_hit(self._game) #if entity is not None, the on_hit method of the entity will be executed

        self._view._dungeon_map.draw_grid(self._game.get_game_information(), self._game.get_player().get_position()) #The dungeon_map is drawn using the game
                                                                                                                         #infomartion and the postion of the user

        if self._task == TASK_ONE: #For Task One
            
            self._view._dungeon_map.update() #Update the dungeon_map, probably needed just for MacOS users
                
            if self._game.won(): #If the game is won, a messagebox will be displayed with the moves_remaining, and the game will be exited
                
                messagebox.showinfo('YOU WON!','WOUW You have finished with {} moves remaining !\n \n'
                                                     .format(self._player.moves_remaining()))
                self._master.destroy()
                            
            elif self._player.moves_remaining() == 0: #If the game is lost, a messagebox will be displayed
                
                messagebox.showinfo('You Lost!','You Lost!')
                
                self._master.destroy()
                

        elif self._task == TASK_TWO:#For Task Two
            
            self._view._dungeon_map.update() #Update the dungeon_map, probably needed just for MacOS users
            
            if self._game.won(): #If game is won

                ans = messagebox.askquestion('YOU WON!','Yes you saved the bird!!! You have finished with a score of {}\n \n Would you like to play again ?'
                                                     .format(self._view._status._second+self._view._status._minutes*60))
                
                self.yes_or_no(ans) #Depending on the answer, game will be exited or a new game will be started
                
            elif self._player.moves_remaining() == 0:
                
                ans= messagebox.askquestion('You Lost!','You Lost, you could not save the bird :-/ ! \n \n Would you like to play again ?'
                                                     .format(self._player.moves_remaining()))
                self.yes_or_no(ans)

                
#---------------------------------------------------- View Class ----------------------------------------------------

                
class View(tk.Frame):
    """ View Class inherits from tk.Frame and which is used to pack the labe, dunegonmap, keypad and status bar."""
    
    def __init__(self, master, gameapp, **kwargs): 
        """Initialise the View Class"""
        
        super().__init__(master, **kwargs) 
        self._master=master
        self._game_app = gameapp
        self._game = self._game_app._game
        self._player = self._game.get_player()
        self._task = self._game_app._task
        
        dungeon=self._game.get_game_information()
        player_position=self._game.get_player().get_position()
        
#-----------------------------------------Label
        
        self._label=tk.Label(master,text='Key Cave Adventure Game',font=("New Times Roman", 24),bg='medium spring green') #Create Label for the game
        self._label.pack(side=tk.TOP,fill=tk.X) 

#------------------------------------KeyPad and dungeon
        
        self._frame_dungeon_pad = tk.Frame(master) #The dungeon Map and keyPad need to be in the same frame, 
        self._frame_dungeon_pad.pack(side= tk.TOP) 
        
        self._keypad = KeyPad(self._frame_dungeon_pad) #The Class KeyPad will inherit from tk.Frame

        if self._task == TASK_ONE: #If Task One, DungeonMap is initialised according to Task 1 specification, else the map is initialised according to task 2
            
            self._dungeon_map=DungeonMap(self._frame_dungeon_pad,self._game.get_dungeon_size())
            
        else:
            
            self._dungeon_map=AdvancedDungeonMap(self._frame_dungeon_pad,self._game.get_dungeon_size())
        

        self._dungeon_map.draw_grid(self._game.get_game_information(), self._game.get_player().get_position())
        
        self._dungeon_map.pack(side=tk.LEFT) 
        
        self._keypad.pack(side=tk.LEFT)
        
#-------------------------------------StatusBar
        
        if self._task == TASK_TWO: #If Task two, displays the statues bar
            
            self._status = StatusBar(master,self._dungeon_map, self._game_app)
            
            self._status.pack(side=tk.TOP,anchor='w')

#------------------------------------------------------------- Status Bar ---------------------------------------
        
class StatusBar(tk.Frame):

    def __init__(self, master, dungeonmap, gameapp , **kwargs): 

        super().__init__(master, **kwargs)
        
        self._master = master
        self._game_app=gameapp
        self._game= self._game_app._game
        self._player = self._game.get_player()

        self._images={'time':'images/clock.gif','lighting':'images/lightning.gif'} #Dic with the name and name of the file for the pictures
        self._squaresize = dungeonmap._squaresize #initialise the size of the 
        
#-----------------------------Button Quit New
        
        self._frame = tk.Frame(self._master,padx=60) #Create a frame for the Button Quit and New
        self._frame.pack(side=tk.LEFT,anchor='n') 
        
        bt_new_game = tk.Button(self._frame,text ='New Game',command=self.new_game)
        bt_new_game.pack(side=tk.TOP,pady=5)
        bt_end_game = tk.Button(self._frame,text ='Quit',command=self.end_game)
        bt_end_game.pack(side=tk.TOP)

        
#----------------------------Time and Timer
        
        self._resizeimages = self.resize_images(self._images, self._squaresize) #Resizing the images for the clock abd lightning image
        self._second=0 #Initialize the seconds
        self._minutes=0 #Initialize the minutes
        
        self._frame_time = tk.Frame(self._master) #Create a frame for the time picture and timer
        self._frame_time.pack(side=tk.LEFT)
        
        self._canvas_time= tk.Canvas(self._frame_time,width=int(self._squaresize), height=int(self._squaresize)) #Create a Canvas in order to create the image of the timer
        self._canvas_time.pack(side=tk.LEFT)
        self._canvas_time.create_image(self._squaresize/1.5,self._squaresize/2.5,image=self._resizeimages['time']) #Create an image of the timer, the scaling 1.5 and 2.5 were used
                                                                                                                #in order to have a status similar to the one given in the brief
        
        self._lab_time = tk.Label(self._frame_time, text ='Time elapsed') #Creatig the label for the timer
        self._lab_timer = tk.Label(self._frame_time, text ='{} m {}s'.format(self._minutes,self._second)) #Timer
        self._lab_time.pack(side=tk.TOP)
        self._lab_timer.pack(side=tk.TOP)
        
        if not self._game.won():#If the game is not won, the timer continues to work
            self.timer()

#-----------------------------Moves Remaining
            
        self._frame_move = tk.Frame(self._master) #Creating a frame for the move picture and remaining move
        self._frame_move.pack(side=tk.LEFT,padx=110)
        
        self._canvas_move= tk.Canvas(self._frame_move,width=int(self._squaresize), height=int(self._squaresize)) #Creating a canvas in order to create the image for the moves
        self._canvas_move.pack(side=tk.LEFT)
        self._canvas_move.create_image(self._squaresize/1.2,self._squaresize/2.5,image=self._resizeimages['lighting']) #Create an image for the moves remaining, scaling was chosen to have
                                                                                                                    # a status bar similar to the one given in the brief

        self._moves_remaining = self._player.moves_remaining()
        lab_move = tk.Label(self._frame_move, text ='Moves left') #Creating label for moves_remaining
        self._lab_move_number = tk.Label(self._frame_move, text ='{} moves remaining'.format(self._moves_remaining)) #Moves remaining
        lab_move.pack(side=tk.TOP)
        self._lab_move_number.pack(side=tk.TOP)

#------------------------------Resize Image
        
    def resize_images(self, dic_images, squaresize):  
        """Method resizes images according to grid size but another scaling has been added to have a status bar similar to the one given in the brief
                Input dic_image(dic) = dictionary containing name and name of the image file
                sqauresize (float) = size of a square in the map"""
        
        for name_image in dic_images:
            image = dic_images[name_image] #Find the name of the file of the image
            image_file = Image.open(image) #Open the image
            image_resize=image_file.resize((int(squaresize/2), int(squaresize/1.3))) #Resize the image
            dic_images[name_image] = ImageTk.PhotoImage(image=image_resize) #PhotoImage is used to display image in canvas

        return dic_images  

#--------------------------Timer
    
    def timer(self):
        """Method to set the timer """
        self.after(1000,self.timer)#After 1000 milliseconds, the definition timer is being called again
        self._second += 1 #add 1 every 1000 milliseconds
        if self._second > 59:#After 59 seconds, becomes 1 minute and 0 second
            self._minutes += 1
            self._second = 0
            
        self._lab_timer.config(text ='{}m{}s'.format(self._minutes,self._second)) #Update the timer
        
        
        
    def new_game(self):
        """Function to create a new game from the GameApp Class"""
        self._game_app.new_game()

    def end_game(self):
        """Function to end a game from the GameApp Class"""
        self._game_app.end_game()

    
                    
#---------------------------------------- Abstract Grid -----------------------------------
class AbstractGrid(tk.Canvas):
    """AbstractGrid is an abstract view class which inherits from tk.Canvas"""
        
    def __init__(self, master, rows, cols, width, height,**kwargs):
        """Initialise the AbstractGrid"""
        super().__init__(master, width=width, height=height, **kwargs)

        
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height
        
        self._x_scale= self._width / self._cols #scaling factor for the x-direction
        self._y_scale= self._height / self._rows #scaling factor for the y-direction
        
        
    def get_bbox(self, position): 
        """ Input tuple of the postion and returns the bounding box for the position"""
        
        row, col = position
        
        x_0 = col * self._x_scale
        y_0 = row * self._y_scale
        x_1 = (col + 1) * self._x_scale
        y_1 = (row +1) *self._y_scale
        
        return (x_0, y_0, x_1, y_1)


    def get_position_center(self, position): 
        """Input tuple of the position and return the coordinates for the center of the cell"""
        
        row, col = position
        
        x_0 = (col+0.5) * self._x_scale
        y_0 = (row+0.5) * self._y_scale

        return (x_0, y_0)

    def annotate_postion(self, position, text):
        """Input position (tuple), and text (string)
            create a text at the position given"""
        
        x,y = self.get_position_center(position) #get the position to create the text
        
        dic={'N':'W','S':'S','E':'D','W':'A'}
        if text =='N' or text =='E' or text =='S' or text =='W': #Becaue the method used to get the commands is from get tags,
                                                                    # it is important to add the tags that the function play can read e.g('WSDA')
                                                                        #Therefore, for commands('NSEW')they have to be converted to ('WSDA')
            
            self.create_text(x, y, text = text, tags=dic[text])
            
        else:
            
            self.create_text(x, y, text = text, tags=text)
        
        
        
#------------------------------------------------- DungeonMap ----------------------------------------------

class DungeonMap(AbstractGrid):
    """The DungeonMap class inherits from AbstractGrid and is used to draw the map of the dungeon"""
    
    def __init__(self,master, size, width=600,**kwargs):
        """Initialise the Class DunegonMap"""
        super().__init__(master, rows = size, cols = size, width = width, height =width,bg='light grey', **kwargs)
        """set the background to light grey"""
        
    def draw_grid(self, dungeon, player_position):
        """Draw the dungeon Map
            input: dungeon(dic) and player_position(tuple)"""
        
        for key in dungeon: #Draw all the entities given in the dungeon dictionary
            entity = dungeon[key]
            dimension_rectangle=self.get_bbox(key)
            self.create_rectangle(*dimension_rectangle,fill=entity._fill)
            self.annotate_postion(key, text=entity._name)
                
        #Draw the player box
        player_bbox = self.get_bbox(player_position)
        self.create_rectangle(*player_bbox,fill='medium spring green')
        self.annotate_postion(player_position, text='Ibis')
        

#------------------------------------------------- Advanced DungeonMap ----------------------------------------------


class AdvancedDungeonMap(AbstractGrid):
    """The DungeonMap class inherits from AbstractGrid and is used to draw the map of the dungeon"""
    
    def __init__(self,master, size, width=600,**kwargs):
        """Initialize the AdvancedDungeonMap"""
        
        super().__init__(master, rows = size, cols = size, width = width, height =width, **kwargs)

        self._images = {'D': 'images/door.gif','player': 'images/player.gif','M': 'images/moveIncrease.gif','K': 'images/key.gif',
                        '': 'images/empty.gif','#': 'images/wall.gif'} #Dictionary for the images, key:Name, Value:Name of Image File
        
        self._size = size 

        self._squaresize = (self._width / self._size) #Scalinf factor for the images
        
        self._images_resize = self.resize_images(self._images, self._squaresize) #resize the images

    
    def resize_images(self, dic_images, square_size):  
        """Method resizes images according to grid size
            input: dic_images (dic)
                   square_size (float)
            return: resize images in a dictionary"""
        
        for name_image in dic_images:
            image = dic_images[name_image] #Find the name of the file of the image
            image_file = Image.open(image)#Open Images
            im_resize=image_file.resize((int(square_size), int(square_size))) #Resize Images
            dic_images[name_image] = ImageTk.PhotoImage(image=im_resize) ##PhotoImage is used to display image in canvas

        return dic_images


    def draw_grid(self, dungeon, player_position):
        """Draw the dungeon Map
            input: dungeon(dic) and player_position(tuple)"""

        #First add the layer of grass over the whole map
        for i in range(1,self._size-1): 
            for j in range(1,self._size-1):
                pos = i,j
                image_pos = self.get_position_center(pos)
                self.create_image(*image_pos, image=self._images_resize[''])
                
        #Second draw the entities on the map
        for key in dungeon:
            entity = dungeon.get(key)
            image_pos = self.get_position_center(key)
            self.create_image(*image_pos, image=self._images_resize[entity.get_id()])
            
        #Third draw the player entity
            
        image_pos = self.get_position_center(player_position)
        self.create_image(*image_pos, image=self._images_resize['player'])
               

##--------------------------------------------------------- KeyPad -----------------------------------------     
        
class KeyPad(AbstractGrid):
    """Widget containing four directional buttons and the class inherits from AbstractGrid"""
    
    def __init__(self,master,width=200,height=100,**kwargs):
        """Initialise the KeyPad Class"""
        
        super().__init__(master, rows=2, cols=3, width = width, height =height, **kwargs)
        self.draw_pad()
        
    def draw_pad(self):
        """Draw the keypad"""
        key_position={(0,1):'NW',(1,0):'WA',(1,1):'SS',(1,2):'ED'} #Dic with position(key) and Direction (One for the Name and One for the Tag which can be used by the function play() (Values)
        
        for key in key_position:
            dimension_rectangle=self.get_bbox(key)
            self.create_rectangle(*dimension_rectangle,tags=key_position[key][1],fill='grey') #For tag uses ('WASD') so it is compatible with the command in the play function
            self.annotate_postion(key, text=key_position[key][0]) #Uses ('NWSE') for the Name of the box 

    

if __name__ == '__main__' :
    
    root = tk.Tk()
    
    app = GameApp(root,dungeon_name='game2.txt',task=TASK_TWO) # YOU CHANGE THE GAME LAYOUT HERE
    root.mainloop()
       

