# Exercise Catalog Web Application

This project is a fully functional exercise catalog application which allows users to view various exercise categories 
and popular exercises within them, including a title, a description, and a YouTube video demonstration. In addition to viewing, users can add, edit, and delete their own exercises. Users must login with Google Sign-In in order to add, edit, and delete. This project fulfills the Item Catalog Application project for Udacity's Full Stack Web Developer program.

## Technologies Utilized

This project was written in Python 2, Flask, SQLAlchemy, and utilizes a PostgresSQL database. The front end is built with Flask
HTML templates, CSS, JavaScript, jQuery, and the application is made fully responsive with media queries and Flexbox.

## Installation

To use this project, first install the below programs:

### Python 2:
Download the [latest Python version 2.7.14](https://www.python.org/downloads/), based on your operating system, and install on your machine. 

### VirtualBox: 
[Install the platform package](https://www.virtualbox.org/wiki/Downloads) for your operating system. You do not need the extension pack
or the SDK. You also do not need to launch VirtualBox after installation.

### Vagrant:

[This program](https://www.vagrantup.com/downloads.html) will download a Linux operating system and run it inside the virtual machine. 
Windows users may be asked to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

### Vagrantfile
This file is included in this repo. After pulling this repo, make sure the Vagrant directory is in the same directory as the Exercise Catalog project. Then, make sure the Vagrantfile is moved into the Vagrant directory. 

From the command line, `cd` into the Vagrant directory and run the command `vagrant up`.  Let it run, this will take a few minutes.

## Configuration

* Logging into the Virtual Machine: using your terminal or git bash, `cd` into the `vagrant` directory and run the command 
`vagrant ssh`.  
* Next, run the command `cd /vagrant` then `ls` and you will see the Vagrantfile you downloaded.
* Download the database [data here.](https://drive.google.com/open?id=1q54oM2LTM3x_dHnCocNjbJfb8Z-iP-ln)
* Unzip the file after downloading. The file inside it is called `exercisecatalog.sql`.  Put this file into the vagrant directory, 
  which is shared with the VM.
* On the command line in the VM, go to `psql` then `CREATE DATABASE exercisecatalog;`
* To load the data into the database: use the command `psql -d exercisecatalog -f exercisecatalog.sql`

Running the above command will connect to your installed DB server and execute the SQL commands in the downloaded file. 

## Running the program & Opening the Application

* `cd` into the directory containing the Vagrantfile, then run `vagrant ssh` to login to the Virtual Machine. 
* `cd` into `/vagrant`
* `cd` into `catalog`
* Run the python file application.py (`python application.py`)
* Once the server is running, go to your web browser and navigate to `localhost:8000/`
* The application should be running and you can now interact with it.

