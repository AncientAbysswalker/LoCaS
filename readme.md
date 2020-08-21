# LoCaS Project
> Parts Cataloging Software

![Example Functionality](https://raw.githubusercontent.com/AncientAbysswalker/LoCaS/master/md/header.gif)

## Working Demo
A working demo can be found at the following for download:

https://github.com/AncientAbysswalker/LoCaS/tree/master/build

## Problem Statement
This project arose from my time with a previous employer. The company I was working with at the time used a number of
legacy systems that were based off of methods and software that were severely outdated. The company worked in the
mechanical sector and was thus involved with parts and parts assemblies. Being able to determine the relationship
between a part number (and revision) and various parameters related to that part was essential, and there was no
convenient and consistent way to do so. As my job often dealt with these areas, my resulting headaches had me consider
whether I could possibly build a solution to help the situation.

## Solution
I decided that it would be invaluable if I were to write a parts cataloging software to display information pertinent
to any given part in a logically organized, readily displayed, and easily navigable manner.

#### Origin of the Name
The shorthand name 'LoCaS' comes as a contraction of my original name for the program - Logical Cataloging Software.

## Implementation

The essential concept that I employed for mechanical assemblies is that every part should have a unique identification
(part number) and iteration on its design (revision number); these help to ensure that information is unique,
identifiable, and traceable. When this is not the case, major issues come to bear with difficulties regarding what
parts are being referred to. Parts can either stand alone, be assembled from other parts, or be used in other
assemblies.

![Example Photo](https://raw.githubusercontent.com/AncientAbysswalker/LoCaS/master/md/001_window.png)

The program acts as a front-end application interface to a SQL database that stores all of the data. The program
shows information on tabs, like a web browser, where each tab corresponds to a part number. For each of these
information fields, the intent is that the field can be updated through the interface. Each tab will show the
essential information regarding the part, including:
* Part Number
* Part Revision
* Part Classification, or type (Purchased Component, Manufactured Component, Assembly, etc.)
* Part Name
* Extended Part Description
* Notes
* Images of the part
* A primary 'Mugshot' image of the part
* List of sub-assemblies and super-assemblies
* List of spare parts and repair kits
* For each of these fields, the intent is that the field can be updated through the interface.

## Nuances of Operation

I tried to keep the user interface ergonomic and fairly simple so that most tasks could be easily accomplished. The UI
operates under several assumptions that are held to the interface. Those are:

* Double-clicking on a text field will open a dialog box to allow you to edit that text field in most cases.
* Clicking on an image in the bottom left grid will open a larger copy of the image, affording a better look at the image and allowing one to
edit the comment for the image.
* Clicking on an entry in the sub-assembly or super-assembly lists will open a tab for that part. If you hold shift,
it will not change focus to that tab.
* Pressing a "+" button will allow you to add an entry to the list or grid the button overlays
* Pressing a pencil button will allow you to edit the entries of the list or grid the button overlays

## Status: On Hold
I have gotten this program to a level of functionality that I am satisfied with. There are still features that I would
like to implement, but I am opting to put this on hold so that I can build my skills in other languages such as
TypeScript and React. Due to the difficulties I have encountered in building this program, I have realized that
building a program like this would be much simpler in a language intended for building applications - namely C#, React,
or Angular.

## Known Shortfalls and Bugs
A current list of bugs can be found [here](https://github.com/AncientAbysswalker/LoCaS/issues)
* Program Login behaviour is currently not implemented.
* Behavior of image dialog is slightly less ergonomic than I'd like, and this should be looked into.
* There is currently no handling for images being physically missing from the database. Such an occurrence currently
causes a full crash of the application

## Planned Features
The project Kanban can be found [here](https://github.com/AncientAbysswalker/LoCaS/projects/1)
* Program Login behaviour is currently not implemented.
* Implement a RegEx type parsing to convert part numbers to a directory structure.
* Implement functionality for opening a parts drawing.
* Clicking on notes in the application should open up a dialog to edit the note
* It is not currently possible to close any tabs.
* Handling to toggle between the revisions for a part number is not implemented yet.
* The problem of configuration files is an area that I have realized is an interesting problem in and of itself.
I've discussed the problem a bit and have some ideas as to what I'd like to do regarding a more full implementation,
but in the meantime I've split configuration between application-specific config (database location, etc.) that
should be restricted to modification by the server application, and user-specific config (whether or not to dismiss
warnings) generated by the program for each new user.
