#!/bin/bash
find . -iname 'test*.py' -exec pytest {} \;
