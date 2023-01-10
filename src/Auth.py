from flask import Flask, redirect, url_for, render_template, request, session

class Auth:
    def __init__(self, vsession = None):
        self.vsession = vsession

    def check(self):
        if self.vsession is None:
            return False
            
        if self.vsession in session and 'administrator' == session[self.vsession]:
            return True
        else:
            return False