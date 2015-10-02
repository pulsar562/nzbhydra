import os
from pprint import pprint
from time import sleep

from flask import Flask, send_file, request
from furl import furl
import requests
from webargs.flaskparser import use_args
from webargs import core, Arg

app = Flask(__name__)


@app.route('/nzbsorg')
@app.route('/nzbsorg/api')
def apinzbsorg():
    if request.args["o"] == "json":
        extension = "json"
    else:
        extension = "xml"
    return handle_request("nzbsorg", request.args.items(), extension, "https://nzbs.org/api")


@app.route('/dognzb')
@app.route('/dognzb/api')
def apidog():
    if request.args["o"] == "json":
        extension = "json"
    else:
        extension = "xml"
    return handle_request("dognzb", request.args.items(), extension, "https://api.dognzb.cr/api")


@app.route('/nzbclub')
def nzbclubrss():
    return handle_request("nzbclub", request.args.items(), "xml", "https://www.nzbclub.com/nzbrss.aspx")
    pass


@app.route('/womble')
def womble():
    return handle_request("womble", request.args.items(), "xml", "https://www.newshost.co.za/rss/")


@app.route('/nzbindex')
def nzbindex():
    return handle_request("nzbindex", request.args.items(), "xml", "https://nzbindex.com/rss")


@app.route('/binsearch')
def binsearch():
    return handle_request("binsearch", request.args.items(), "html", "https://www.binsearch.info/index.php")


def remove_if_exists(list, key):
    if key in list:
        list.remove(key)


def handle_request(provider, argsitems, extension, baseurl):
    args = {}
    for i in argsitems:
        args[i[0]] = i[1] 
    keys_sorted = sorted(args.keys())
    remove_if_exists(keys_sorted, "apikey")
    remove_if_exists(keys_sorted, "o")

    filename = provider
    for arg in keys_sorted:
        filename = "%s--%s-%s" % (filename, arg, args[arg])
    filename += "." + extension
    if not os.path.exists(filename):
        print("Cannot find cached respose " + filename)
        f = furl(baseurl)
        for key in args.keys():
            f.add({key: str(args[key])})
                
        print("Requesting URL " + f.tostr())
        r = requests.get(f.tostr(), verify=False)
        if r.status_code != 200:
            return r.text, 500
        with open(filename, "wb") as file:
            file.write(r.content)
            print("Wrote cache response from " + f.tostr() + " to file " + filename)
    
    if os.path.exists(filename):
        if extension == "json":
            print("Sending " + filename)
            return send_file(filename, "application/javascript")
        if extension == "xml":
            print("Sending " + filename)
            return send_file(filename, "application/xm")
        if extension == "html":
            print("Sending " + filename)
            return send_file(filename, "text/html")    
            
        
        return "Unknown request", 404


if __name__ == '__main__':
    app.run(port=5001, debug=True)