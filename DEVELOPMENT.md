# Virtual Machine Setup

Now slightly easier than before, you will need:

* http://virtualbox.org - Virtualbox (A virtual machine)
* http://vagrantup.com - Vagrant (A virtual machine manager)

Once you have those installed (Windows, Mac, Linux, doesn't matter) go into the directory you've checked out Lampstand to (the same one Vagrantfile is in) and type

`vagrant up`

First time you do this will take a while, because it'll download an image of ubuntu, then set it up, then add all Lampstand's Debian packages and Python packages. Finally it downloads a metric fuckton of Natural Language data. It's really bad at output buffering, so it will look like it's dead, it almost certainly isn't.

Once it's finished, it'll give you back your prompt. You can then go into the server by using

`vagrant ssh`

which will log you in.

You can also connect to the server over ssh by connecting to localhost port 2222. (If you have more than one Vagrant machine active, this won't work. Vagrant Up's output will tell you the right number) username/password "vagrant/vagrant"


To shut it down, `vagrant halt`, to delete it `vagrant destroy`. Because this never touches the code, the only things you'll lose are stuff in the MySQL database.


## Exposed Ports & Services

This VM will install an IRC server, running on the VM port 6667. This is exposed to your actual machine - the parent machine - as localhost:6667 (The default IRC port), so you should be able to open localhost as an IRC server in your favourite client once the server is up.

The server's also running mysql, username/password "webapp/webapp", mysql root password is 'iMPOrTanT'

The "vagrant" user has full sudo access.

# Lampstand Setup

## Config 

Lampstand reads defaults.ini first, then overrides with any values in config.ini in the same directory. Part of the vagrant up process will copy config.dev.ini to be config.ini, which contains the right database and server details to run properly in the VM. Once it's created, you should add your name as an admin, so you can run admin commands. 

## Development

Your parent computer's code repository for lampstand is shared on the VM as /vagrant, any changes you make there will automatically be reflected on the server. You can get Lampstand to reload any reactions module by `/msg lampstand reload [modulename]` as an admin (This also resets the overuse/cooldown numbers), but any changes to lampstand.py will need a restart.

## Starting the server

To start the server from inside the VM, you need to activate the virtual environment for python, go into the code directory, and run the server.

```
workon lampstand
cd /vagrant
./launch.sh
```

To stop it, ctrl-C.

If you get an error in the definitions module about dictd, execute `toggleglobalsitepackages` and the message should be "Enabled global site-packages". I need to work out why this doesn't stick.

(Almost every python module being used is from PyPi, except the access to the UNIX Dictionary Service, for which the python module documentation is - I kid you not - on a GOPHER server. So it's installed from debian package management, with regret.)

Any questions, ask in `#lampstand` on irc.esper.net
