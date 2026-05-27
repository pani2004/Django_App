from .base import * 

DEBUG = True

# Prototype/dev: avoid validator import edge cases in Docker reload cycles
AUTH_PASSWORD_VALIDATORS = []
