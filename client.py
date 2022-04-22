from asyncio import sleep, wait
from asyncio.windows_utils import Popen
from logging import root
from os import popen
import threading
import time
from tkinter import *
from tkinter import messagebox
import tkinter
from turtle import end_fill
from xmlrpc.client import ServerProxy




proxy = ServerProxy('http://localhost:5000')
root = Tk()
inputlist = [] #List for storing user inputs for later use



def init_gui():
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.title("Wikipedia Crawler")
    root.geometry("600x300")

    message ="Welcome,\n\nType in two articles, and \npress the button to search the\nshortest path between them.\n\n\nIf there's an error during the\nprocess, it will be displayed\nhere!"
    

    text_box = Text(
        root,
        height=15,
        width=30
    )
    text_box.insert('end', message)
    text_box.config(state='disabled')
    text_box.place(x = 300, y = 30)

    


    #myLabel = Label(root, text="Welcome, type in the articles you want to crawl and press the button.")
    #myLabel.pack()

    article1 = Label(root, text = "Article 1").place(x = 30,y = 50)  
    article2 = Label(root, text = "Article 2").place(x = 30, y = 90)

    

    T1 = Entry(root)
    T2 = Entry(root)

    def ButtonPress():              #In this function I'm saving the user inputs into a list and then redirecting the program to run main()
        inputlist.clear()

        input1 = T1.get()
        input2 = T2.get()
        inputlist.append(input1)
        inputlist.append(input2)
        main()

    Button(root, text = "Search for articles", command=ButtonPress, activebackground = "pink", activeforeground = "blue").place(x = 100, y = 130)  



    T1.place(x = 80, y = 50) 
    T2.place(x = 80, y = 90)

    root.mainloop()





#https://stackoverflow.com/questions/45441885/how-can-i-create-a-dropdown-menu-from-a-list-in-tkinter

#creating a dropdown menu constisting of the wikipedia articles found based on the users input
def create_dropdowns(article_list, two_articles):
    print("DEBUG INSIDE CREATE_DROPDOWNS-FUNCTION")

    newWindow = Toplevel(root)

    variable = StringVar(newWindow.geometry("400x200"))
    variable.set(article_list[0][0]) # default value

    variable2 = StringVar(newWindow.geometry("400x200"))
    variable2.set(article_list[1][0]) # default value


    w = OptionMenu(newWindow, variable, *article_list[0])
    w.config(width=50)
    w.pack()

    w2 = OptionMenu(newWindow, variable2, *article_list[1])
    w2.config(width=50)
    w2.pack()

    two_articles.clear()

    def ok():

        two_articles.append(variable.get())
        two_articles.append(variable2.get())
        print("DEBUG INSIDE OK-FUNCTION")
        newWindow.destroy()

        pass
        
    button = Button(newWindow, text="Crawl", command=ok)
    button.pack()
    #this enables for the create_dropdowns-function to run until the button is pressed
    #so that the main-function doesn't continue to run without any returns
    root.wait_window(newWindow)
    return two_articles

def main():
    
    print("DEBUG INSIDE MAIN-FUNCTION")
    message ="Welcome,\n\nType in two articles, and \npress the button to search the\nshortest path between them.\n\n\nIf there's an error during the\nprocess, it will be displayed\nhere!"

    text_box = Text(
    root,
    height=15,
    width=30
    )
    text_box.config(state='disabled')
    text_box.place(x = 300, y = 30)
        

    article_list=[]
    two_articles = []


    if (inputlist[0] == '' or inputlist[1] == ''):
        #print("AAAAAAAAAAAAAAA")
        text_box.configure(state='normal')
        text_box.insert("end", "Please provide inputs on both fields.")
        text_box.configure(state='disabled')
        return
    
    
    article_list = find_articles(inputlist)
    


    if (article_list[0] == [] or article_list[1] == []):
        if article_list[0] == []:
            text_box.configure(state='normal')
            text_box.insert("end", "No articles found on '{}'. Type in another article name.".format(inputlist[0]))
            text_box.configure(state='disabled')
            
        else:
            text_box.configure(state='normal')
            text_box.insert("end", "No articles found on '{}'.\n Type in another article name.".format(inputlist[1]))
            text_box.configure(state='disabled')
        
        return

    
    try:
        two_articles = create_dropdowns(article_list, two_articles)
    except Exception as e:
        return e

    find_shortest_path(two_articles)

    init_gui()
    


def find_shortest_path(A):
    
    A1 =A[0]
    A2 = A[1]
    start = time.time()
    newWindow2 = Toplevel(root)
    variable1 = StringVar(newWindow2.geometry("500x300"))
    
    text = Text(newWindow2, height=15, width=40)
    text.pack()
    try:
        try:
            shortest_path = proxy.find_shortest_path(A1, A2)
            end = time.time()
            text.configure(state='normal')
            text.insert("end", "\n************************\nPath found!\n\nThis process required {} steps.\n\nTraversed articles: {}\n\nTime taken to complete: {} seconds\n************************\n".format(len(shortest_path)-1,shortest_path, end-start))
            text.configure(state='disabled')
        except Exception as e:
            text.configure(state='normal')
            text.insert("end", "An error has occurred on the serverside: {}\n".format(e))
            text.configure(state='disabled')
    except KeyboardInterrupt:
        print("Process interrupted.")
        exit(1)
    
    def ok():
        print("DEBUG INSIDE OK-FUNCTION")
        newWindow2.destroy()

        pass
        
    button = Button(newWindow2, text="OK", command=ok)
    button.pack()

    #this enables for the create_dropdowns-function to run until the button is pressed
    #so that the main-function doesn't continue to run without any returns
    root.wait_window(newWindow2)





def find_articles(inputlist):                                        
    articles = proxy.find_articles(inputlist)
    return articles




def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()


if __name__ == '__main__':
    init_gui()
    #main()