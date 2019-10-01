# LoCaS Project

## Problem Statement
This project arose from one of my previous career positions. The company in question was very averse to change, and part of that meant that all of the software, databases, and parts information was based off of methods and software decades superceded. As my job dealt extensively with many of these areas, my resulting headaches had me thinking - "for sure I could make something better than this‽"

## Solution
I decided to try my hand at making a sort of parts-cataloging software, to display the information that, in my experience, is very useful and should be readily accessible - which it unfortunately was not. I decided that the data should be logically organized and readily displayed in a way that it is easy to navigate and find out what parts inherit from others - which is also something that was a nightmare to try to figure out. Thus was born the name - Logical Cataloging Software, or LoCaS. Honestly a bit uninspired, but at least it's easy to say...

The vision for this project and the structural logic is outlined in the following points. The features and vision below will be implemented incrementally as I have time.

Logic
* The essential idea behind mechanical assemblies is that every part should have a unique identification id (part number) and iteration on its design (revision number). These help to ensure that information is unique, identifiable, and traceable. When this is not the case, major issues come to bear with difficulties regarding what parts are actually being referred to.
* Parts can either stand alone, or can have inheritance: assemblies (what I call super-assemblies) can inherit from stand-alonme parts or other sub-assemblies
* Parts of the same part number but different revisions are most often part of the same assemblies, but due to how things are not always so clean-cut I have opted to handle revisions individually.

Function
* The program can open multiple parts in parallel, controllable by the tabs on top.
* Each parts panel will contain essential information regarding the part, including:
  * Part Number
  * Part Revision
  * Part Classification (type, like Purchased Component, Manufactured Component, Assembly, etc.)
  * Part Name
  * Extended Part Description
  * Notes
  * Images of the part
  * A primary Mugshot image of the part
  * List of sub and super assemblies
  * List of spare parts and repair kits
* For each of these fields, the intent is that the field can be updated through the interface.
* Eventually I believe I will add more features to track full parts assemblies using a tree type architecture

## Known Bugs
* The PDF open button still receives focus even though it should not
* Behavior between multiple tabs is not intended to function yet. Some features, like adding images, may work. They also may break the same features on the sample tab... -_-
* The '+' button to add images is tied to the wrong frame, and as such it scrolls down when there are enough images to allow scroll.
* Scaling formula for the images in the dedicated image dialog are a bit wonky; this will need to be tweaked
* There is currently no handling for images being physically missing. Such an occurrence currently causes a crash
* There is some duplication in image handling for the image display dialog that will need to be addressed