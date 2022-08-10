# PROMO UTN

## video demo: https://youtu.be/s1OC_moTfm8

## description
this is a web application, structured with the framework flask, that will make things easier to the promo members from my year.
They now are going to be able to organize parties, selling those party's tickets, checking Guest list, and so on.
it has 3 main functions:

-the parties section: where you as a promo member will be able to propose parties, voting proposals and checking the lists. As normal accounts you will be able to see the parties info, and it's tickets.

-the memebers section: here you will find the promo members, their images and a redirect to their instagram accounts.

-the annonym messages section: it's kind of a billboard where you put up any message anonymously.

## explanation
### file1 - app.py
this is the nucleus of the application. here we have all the diferent functions that calls the html pages, which execute SQL querys on the db file, and also uses some functions from helpers.py.
#### some general specifications
the functions generally return the "render_template" functions with info about the user included because of that info is required in the "layout.html" file, which is always running on.
#### global1 - flask configuration
configurates the application as templates autoreloadable, with sessions permanents, and a session type as "filesystem", that means that the session information is going to be saved in the user's computer in order to be autologged.
#### global2 - sql configuration
links the varable "db" to the database file "promoutn.db".
#### function1 - index()
this function collects some info from the database. these are:
the user data, for this the server detects if the user hasn't had logged in, in which case the server will only save his type and id as "invitado" ("guest").
messages which have been sent anonnyimously.
jodas(and in which of them the user had bought tickets).
promo members's information.
the server collects this data running some "SELECT" queryes on the database file.
Then returns a function to render the template with the "index.html" template name, and the collected info.
#### function2 - login()
When the user logs his account in.
when the user ends up here with the "GET" method the function returns a "render_template" function with the "login.html" template name. Else if the method is "POST" the server request the form answers and, after checking if there are no blank spaces, ensures that the username exists and the password hash matches the correspondent one in the database, if everything is correct tells to the computer the user id and will be able to ask her back it later.
#### function3 - logout()
Tells the computer to forgive the user id awardaded earlier.
#### function4 - register()
When the user registers himself in an account.
If the user ends up here with the "GET" method the server will returns a "render_template" function with the "register.html" template name on it. Else if the method is POST means that the user had submitted the form so the server request the form answers and, after checking if there are no blank spaces or if the two password doesn't match, ensuring that the username doesnt exists (the server does it with this tricky try-except where the error will only be raised if the list "userswiththatname" is empty, meaning there is no one registered with that name. An easier solution would have been using the len() function and check the emptiness that way)Checking the wellness of the password (calling a function from "helpers.py" which will return ok in case it's well) the server will save the user info using an "INSERT" query to the "usuarios" table of the database, and then redirects the user to the home page.
#### function5 - solicitar()
this is the way that normal accounts have to ask for the admin to turn his account into a promo type account.
If the user ends up here with the GET method the function returns a "render_template" function with the "solicitar.html" template name, and userdata on it. Else if the method is POST means that the user had submitted the form, so the server request the form answers and, after checking if there are no blank spaces, inserts (using the INSERT sql query) the answers into the "promos" table, and update the account type to be "solicitante"(applicant).
#### function6 - confirmar()
when the admin allows an applicant to be a promo.
This function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py". It requests the form answers and updates the "SEGUIDORES" column from the PROMOS table with the input value, and the "tipo"(account type) to be "PROMO" in the "USUARIOS" table.
#### function7 - eliminarpromo()
Turn a promo account back into a normal one.
this function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py". It requests the user id input value and, after checking if there are no blank spaces, deletes the row FROM the table "promos" where the user id is equal to the one given, and turns back the "tipo" to normal in the table "usuarios" where the user id is equal to the one given.
#### function8 - anonnyms()
when a logged user submits an anonnym message to the board.
this function requires the user to be logged, using the "login_required" decorated function from "helpers.py". it requests the message input value and, after checking if it's not empty, inserts into the table annmsj the whole message, the emisor id(yeah, not too anonnym huh) and the datetime. Ends by returning a redirect function to the homepage.
#### function9 - elimnarmsj()
when the admin deletes a message which doesn't want to be out there.
this function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py". It requests the message id hidden input and, after checking if there are no blank spaces, deletes the row from the table annmsj where the message inpuy equals to the one given. Ends by returning a redirect function to the homepage.
#### function10 - alistarse()
When the user buys a ticket for a party.
This function requires the user to be logged, using the "login_required" decorated function from the file "helpers.py".
When the user ends up here in a GET method, the function will return a "render_template" function with the "confirmarlista.html" template included and some information about the user and the party included in the lists of dicts called "userdata" and "jodadata" respectively, and a variable that contains a value which expreses whether if the user hasn't already confirmed the party(the server gets this value with a raise-except argument where is only going to be raised an error if the user wasn't in the list of that party).
else, when the user ends up here with a POST method, it means that the user had clicked on the confirm form to buy the ticket. The function first makes sure that the party hasnt had run out from tickets (comparing the "capacidad" variable from the database with the lenght of the list of people whom had confirmed) then if the user is not a promo or admin, checks if has enough money, then checks if he hasn't had already confirmed before (with the try-except trick where there will be only raised an exception if the list "listaid" is empty). Afterwards makes sure to only charge people who aren't promo members or admins, and charges them updating the database setting the cash to be the previous cash minus the ticket's price, and then adds his userid, and party id to a database with all the party's confirmed people. ends by redirecting to the homepage.

#### function11 - listajodas()
Here appears the guest list for a certain party.
this function requires the user to be a promo member, using the "promo_required" decorated function from the file "helpers.py".
It asks for the joda id in the args, and calls all the confirmed people from the table "listas" where the jodaid equals to the one given in the args. also calls from the database some information about the party.
This function returns a "render_template" function whith the "lista.html" name template,and the list of confirmed people also with some info about the party included.

#### function12 - buscarconfirmados()
In the previous route, "/listajodas" the promo members will take ages searching for a certain guest, in order to accelerate that proccess there is this function wich will return a jsonifyed version of a list with only the confirmed persons which has an id similar to the one typed.
this function requires the user to be a promo member, using the "promo_required" decorated function from the file "helpers.py".
It recalls the list of persons which has an id similar to the one which is requesting with the "request.args.get" function concattenating with a "%" symbol at the end (this way all the id which has any characters after that number will be included too). after saving that information in a variable called confirmados, returns a jsonifyed version of that list.

#### function13 - ya_entro()
to make sure that nobody gets in with the same id than other person this function is a kind of a checker, with this function you can "tic" the people which have already entered.
this function requires the user to be a promo member, using the "promo_required" decorated function from the file "helpers.py".
It requests the "listaid" value ensuring that has been given and updates "listas" table, setting the "yaentro" column to be "si" where the listaid value equals to the one given. Then returns a redirect function to the previous list where the user was(thanks to its in a get method, the process of going back consists in just configurating the link).

#### function14 - eliminarconfirmado()
when the admin, for a given reason, deletes a confirmation from an user who doesn't want to be there.
this function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py".
The function requests the list id and, after checking if there are no blank gaps, deletes the user row from the table "listas" where the list id is equal to the one given. Ends by returning a "redirect" function to the homepage flashing a message to remind the admin that the user has paid for being there.

#### function15 - proponerjoda()
When a Promo member proposes a party.
this function requires the user to be a promo member, using the "promo_required" decorated function from the file "helpers.py".
Sets a list of "dicts" with all the data that has to request, and the type of input that it has to have.
When the user ends up here in a GET method, the function will return a "render_template" function with the "proponer.html" template included, the list with the requests, and some information about the user in the list of dicts called "userdata" which recall the user information from the database abreviated as db.
else, when the user ends up here with a POST method, it means that the user had clicked on the submit party button, proposing a party. The function starts to request the form answers checking that there are no blank spaces in the form. Then saves all the answers in the "jodas" table from the database. ends by redirecting to the homepage with a flash message telling that the party has been succesfully proposed.

#### function16 - votarjodas()
when a promo member votes for a party
this function requires the user to be a promo member, using the "promo_required" decorated function from the file "helpers.py".
When the user ends up here in a GET method, the function at first will check that the user hasn't voted yet, then will calculate some information about the party with the info from the database (such as how much each member has to pay for the budget of the party and how much will they win in total if they sell the 80% of the tickets) then also gets from the database how much promo members had already voted, how much voted yes, and how much voted no (The server calculates this getting first the total list of votes in the variable bdvotos, then sets a dict with 2 counters and, with a for bucle, loops on the votes from bdvotos, and adds up to the counters of the dict properly). Then returns a "render_template" function with the "confirmarlista.html" template included and the info collected recently.
else, when the user ends up here with a POST method, it means that the user had clicked on the vote button for voting the party. The function first makes sure that the vote isn't empty, and inserts into the "jodavotos" table the value of the vote, and the user id of the voter. The server also takes advantage of the fact that this function will be executed whenever a promo member votes so it also checks if the votes are not enough to confirm or reject the party (does it by running the function "chequearvotos" from the file "helpers.py"), in positive case it charges the promo members the calculated amount(by running the "restarles" function from the file "helpers.py"). Ends by redirecting the user to the homepage

#### function17 - eliminarjoda()
when the admin, for a given reason, deletes a party from the database which doesn't want to be there.
this function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py".
The function requests the form answers and, after checking if there are no blank spaces, deletes the party row from the table "jodas" where the joda id equals to the one given. Ends by returning a redirect function to the homepage.

#### function18 - pedircarga()
When an user wants to load money.
this function requires the user to be logged, using the "login_required" decorated function from "helpers.py".
If the user ends up here in a get method, returns a "render_template" function from the file "helpers.py" with some user data.
Else when the user ends up here with a POST method, it means that the user had clicked on te confirm button from "pedircarga.html", so then vonfigurates a link so it guides the user to the whatsapp chat with the admin with some text prescripted, and makes the web browser open a new tab on that configurated link. Ends by returning a redirect function to the homepage.

#### function19 - cargarplata()
When the admin has agreed with the user who is going to charge money.
this function requires the user to be an ADMIN, using the "admin_required" decorated function from "helpers.py".
If the user ends up here with a GET method, returns a render_template function with the "cargarplata.html" template, and information about the user.
Else if the user ended up here with a POST method, means that has already submited the form so, the server requests the charged user's id and the amount to charge, recalls from the database the amount of money that he currently has, and updates his cash to be the previous money added with the deposit one. ends by redirecting the admin to the home apge.

### file2 - helpers.py
In this file we can find some helpful functions that are going to be used in the nucleous program, and that will help to keep that file clean.

#### function1 - login_required()
This function returns a decorated function that in case there is no user id loaded, redirects the user to "/login".
#### function2 - promo_required()
This function returns a decorated function that in case there is an id charged which in the database hasn't a "tipo" column equals to "Promo" or "Admin" will redirect the user to the homepage.
#### function3 - admin_required()
This function returns a decorated function that in case there is an id charged which in the database hasn't a "tipo" column equals "Admin" will redirect the user to the homepage.
#### function4 - checkwellnes()
ensures that the password introduced meets the necessary requirements.
this function receives a string called password, first detects if it's length isnt in between 6 and 16, in true case returns a message letting the user know that requirement. Then with a for bucle counts how many numbers and letters the password has, if hasn't more than 3 letters or numbers returns a message letting the user know those requirements. If all the requirements are met the function returns "ok".
#### function5 - restarles()
When a party is confirmed each promo member is charged with the amount correspondent to the party budget.
The function receives a "jodaid" integer, recalls the budget from the table "Jodas" saving it in a variable called "presupuesto", and all the users ids and his respective amount of cash.
Calculates how much each member has to pay dividing the budget in the lenght of the promos list saving it in a variable called CUpone, and with a for bucle looping around each promo member in the list of dicts "promos" update his Usuarios table row, sets the cash column to be the respective previous amount of cash minus the CUpone value.
##### function6 - confirmarjoda()
recalls the joda name from the table jodas saving it in a variable called nombrejoda, Updates the "estado" of the party to 'confirmada', and inserts into the table "annmsj" a message telling that the party has been confirmed with an emisor's id as 0.
##### function7 - eliminarjoda()
recalls the joda name from the table "jodas" saving it in a variable called "nombrejoda", Deletes the joda's row and the joda vote's rows from the database, and inserts into the table "annmsj" a message relling that the party has been deleted with an emisor's id as 0.
#### function8 - chequearvotos()
Checks how are the votes of a party in discussion going, in case that the votes are enough the function confirms or deletes the party.
The function sets a list with all the promo members ids and list with all the votes and starts counting. In a dict called votes sets 2 counters, the postives and the negatives votes. with a for bucle iterating the list of votes adds up to the counters respectively.
Then compares: If the positive votes represent more than the 80% of the promo members calls confirmarjoda and returns True. Else if the negative votes represents more than the 20% of the promo members, the function calls eliminarjoda and returns False. if none of the conditions are met just returns false.
#### function9 - chequearfecha
recalls the party date from the database and configurates the string to be comparable with the today's date, if this is bigger that the joda date then calls the function "eliminarjoda" to delete it, and returns True. Else if yet isn't bigger returns False.
### file3 - promoutn.db
It's the Database where all the info is almacenated, is divided in the following tables:
#### table1 - usuarios
Here is almacenated the information about the user,
the columns are: "id" wich is going to be the key number for each user, "nombre" where will be almacenated the user's full name, "username" where will be almacenated the user's username, "password" where will be almacenated the password hash, "tipo" where will be setted the user's accounts type (can be "normal"(default), "promo" or "Admin"), "cash" Where is going to be the amount of money number that the user currently has in his account.
#### table2 - annmsj
In this table are almacenated all the messages that are sent.
It's columns are: "msjid" here will contain key value for each message, "userid" the message's emisor id (it's not so anonym hehe), "mensaje" here will be almacenated the body of the message, "hora" the time at which the message has been sent.
#### table3 - jodas
This table contains all the information about the parties confirmed and also in debating process.
#### table4 - jodavotos
Here are going to be all the votes for a debated party,
It's columns are:"jodaid" the key value for each vote, "userid" the id of the user which has made that vote (its not a secret vote hehe),"voto" which is going to be the value that determines if the vote is positive or negative.
#### table5 - listas
In this table are almacenated the users that had confirmed their presence in a party.
The columns the table contains are: "listaid" key value for manipulate each row, "jodaid" this is the id of the party which has been confirmed, "userid" contains the id of the user who had confirmed,"yaentro" here is going to be the info which tells if the user has had already get in the party.
#### table6 - promos
Here is going to be almacenated the extra info required for those accounts of the people who are promo members.
the columns that contains are: "userid" the id of the user account, "instagram" will save the promo account owner's instagram accounts links, "foto" will save a link to a photo of the promo member. "seguidores" here are going to be saved the amount of the promo account owners instagram accounts followers.

### file4 - requirements.txt
Here are simply specified the requirements which the program needs to initialize the web application, as the flask documentation clarifies.
### folder1 - templates
In this folder are saved all the templates which are going to be used along the web app.
#### template1 - layout.html
This is going to be the schema of all the other templates, contains a jinja openable block so other files can insert html in there.
In the "head" contains some configuration, some links to bootstrap, and to the style "css" file called "styles.css".
In the body contains a nav bar where are going to be acceses links to functions such as login or register if the user is not logged, and if he is logged contains a "pedir carga" access(or "charge others" if the user is an Admin),"soy promo" access (in case that the account type isn't already "promo"), and a "log out" access.
In the body, also is included a section where will appear the flashed messages in case of any.
The openable block, "block main",where other files will insert more html.
And a footer section where is only a copyright element.

#### template2 - index.html
This file contains the sections aside (where is included the "messages" functions), and the section content (where are going to be the functions "jodas", and "promos"). This organization will help to the stylization, and the correct movement of the fixed element "messages".
Extends the "layout.html" file in the specific space "block main".
##### function messages
Its divided in 2 divs, in the first one are going to be all the messages displayed with a "for bucle" where in each message contains the message and the hour (if the sender of the message is the SERVER there is a header message which clarifies that). If the user type is Admin there are showed the names of the emisors and a form to delete the message, this button has an action in "/eliminarmsj" with a POST method so when the admins submit the form the hidden input msjid is sent to the function "/eliminarmsj".
In the other div there is a command section where is going to be included a form with an input for the message that the user wants to write, a submit button which will send the input value to the function "/anonnyms" with a POST method.
##### function jodas
In an inner div,"jodas" displays all the current parties there are, for each party div first asks if the party is confirmed or if the user is a promo or an admin, the other possible case is that the party is not confirmed and the user is not a promo member so its okay to the party not being displayed. Inside each party divthere are some general spans like the name, description, etc. And some functions will be shown dependending on the if conditions;
If the party is confirmed, there are two conditions more: If the "jodaid" is in the list of parties which the user had confirmed, then just shows an "confirmado" span, else will show a form to confirmate, when youhit click on it is submitting a jodaid hidden input to the "/jodas_alistarse" function in the method get; The other subcondicion is that if the user type is "Promo" or "ADMIN" will be shown a form which when you hit click on it, its submits a "jodaid" hidden input to the function "/listajodas" in a get method.
Else when the party is not confirmed, it means that the upper condition (line 43) has only given true in the second condition, so we can be sure that the inside of this one else sentence will only be showed to the promo members or admins. It just shows a vote form which when you hit click on it you submit a "jodaid" hidden input to the function "/votarjodas" in a get method.
Independently on wheter if the party has been confirmed or not, there is this last condition which is true if the user is an admin and displays a delete party form which on where if the user hits click it submits a "jodaid" hidden input to the "/eliminarjoda" function with a POST method.

##### function promos
Is the section where all the promo members are presented.
At first it initialize a counter in 0, in a div called confirmados will contain divs called "4promos" and will begin a for bucle going promo by promo (or solicitant) and it will displays the person's div if the promo type is "PROMO" or if the user type is "ADMIN", so the only cases it won't display the div is when the user is not an Admin and the member is not confirmed, which is ok.
The bucle starts with a condition, if the counter has arrived to 4 then closes the div "4promos" and initialize one again, resetting the counter to 0. Then presents some promo into the promo div, has an link to the person's instagram account, inside the link you can find the person's photo, and a span with his name. If the user is an Admin an eliminate promo form will be shown, and also a confirm solcitant form if the person is an applicant. both forms sends the promo id hidden input to "/eliminarpromo" and "/confirmar" respectively with a POST method.
Before the bucle restart adds 1 to the counter value. voila!

#### template3 - register.html
Is a simple form with simple inputs, such as "nombre", "username", "password", "confirmation", it submits the inputs to the "/register" function with a POST method

#### template4 - login.html
An even simpler form, just contains a "username" and "password" inputs, its submits the inputs to the "/login" function with a POST method.

#### template5 - proponer.html
Not a so basic form this time, it's inputs are displayed with a jinja for bucle looping around the requests in the list "solicitudes". In the "sevende" request there is an exception beacause its a "select" input. when the form is submitted it sends the inputs values to the function "/proponerjoda" with a POST method.
#### template6 - votacion.html
In a paragraph is shown all the info that came in the "jodadata" variable. then there is the amount of voters, and "yes voters" shown with a bootstrap progress bar.
Afterwards a form With the radio inputs for yes or for no, with a button which submits the vote and the hidden jodaid input to the "/votarjodas" function with a POST method.
#### template7 - pedircarga.html
A simple form with an amount cash input which submits the amount to the "/pedircarga" function with a POST method.
#### template8 - cargarplata.html
A simple form, with an destiny id an amount cash input, which submits the amount to the "/cargarplata" function with a POST method.
#### template9 - confirmarlista.html
In a paragraph is shown all the info that came in the "jodadata" variable.
Afterwards a conditional where if the the "confirmado" variable value is "si" there is a span saying that the user had already confirmed, with a link to index page.
Else there is shown a form with a "jodaid" value charged in a hidden input which will be submitted to the function "/jodas__alistarse" with a POST method.
#### template10 - lista.html
Without any user interaction the page contains an unordered list which contains all the confirmed people, displayed with a for boocle iterating each row of the list "confirmados".
When the user types something in the "userquery" input, there is an event listener which gets activated and asks from the subpage "/listajodas/buscar" the jquery of the people which has an id starting by the input typed. fter that call the variable called "html" gets updated in a for bucle iterating around the jquery returns, and the inner html of "lista__confirmados" gets repalced by the updated variable "html".
#### template11 - solicitar.html
it's a form requiring a link for the instagram of the future promo member account owner, and a link for a photo, accompanied with a link to a web explaining how to configurate the photo link, will submit the input values to the function "/solicitar" with a POST method
### folder2 - static
this has some useful images wich are called from different html files, and a style configuration.
#### file1-avioncitopapel.png
it's a paper plane used to be the icon for submit a message in the annonym messages section.
#### file2-escudoutn.png
it's the logo of the page used in the nav bar as a link for the home page.
#### file3-escudoutn.svg
it's the logo of the page used in the html head as the icon.
#### file4-promo22.jpg
It's a photo of the promomembers, is used as a background to the "jodas" section.
#### file5-styles.css
Is a style configuration linked in the html head with a many lot of styles decition, Some of the ones that need more explanation are:
##### general
the content div has a minimum height of 100vh this way the footer will always start behind the lenght of the page. This div has a margin bottom equals to the length of the footer so is possible to be shown, and has a shadow effect so it seems like it's upper than the footer.
The footer has a fixed position so it will be 5px above the bottom of the page, it's usually covered by the content div, but when its scrolled down, the content div moves up, and in that 5px margin the footer is shown.
##### Message section
For this section, i have made first a container aside which will be 100% long so then the sticky div subcontainer div will be sticked all along the page, Inside the "mensajes" section has a calculated heigh which will be the 100 percent available minus the heights of the nav, the "escribir" div, and of the flashed message if any(checks if there is a flashed message with a an extra class added only if the jinja "if" sentence is true).
##### jodas section
Each party has a background image declarated as the promo members photo, an a fixed attachment, so the photo stays quiet iven if the user scrolls the page. each element is positionated with position absolute.
##### promos section
Each promo member div has their image inside another container which will be useful to cut the photo, this way all the photos have the same proportion. When the image is from an applicant it means it has to have a shorter height so the inputs and buttons can fit in. The height is modified when the jinja adds a class to the div which is "promo__foto__solicitante".
