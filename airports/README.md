This Demo folder contains a collection of small scripts with examples about
how to create an interactive application using bokeh AjaxDataSource and 
a simple flask server.

This demo uses the free airports, flights and routes data at:
https://github.com/jpatokal/openflights.

Examples included:


airports_simple
===============

Simple script that shows a world map and circle glyph for every airport in the world.
This example is a sort of very simple example to be used as base for the others
examples, that demonstrate a gradual evolution in terms of features and complexity.

To hold the data, it uses the most commonly used ColumnDataSource.

To run the script execute:

>> python airports_simple.py


airports_ajax
=============

This example show a different implementation of the airports_simple
example using AjaxDataSource instead of ColumnDataSource.

It also differentiates the airports and shows the airport with more
destinations routes in red, all it's destinations in green all other
airports with a smaller circle in light grey color. This airport is
also connected to all it's destinations using a line glyph.

To run the script execute:

>> python airports_ajax.py


airports_ajax_animated
======================

This example shows how to use an AjaxDataSource to drive live animations
on a bokeh plot. It changes the selected airport every 3 seconds and 
shows all the airport destinations with green circles.

To run the script execute:

>> python airports_ajax_animated.py


airports_dashboard
==================

This example shows a basic interactive dashboard where users can see all the
airports in the world and use tap tool to select a new airport. When the new 
airport is selected it turns into a red circle and all it's connections to
green circles. Other airports are rendered as small lightblue circles if they
have connections and as tiny lightgrey circles if they have no destinations.

NOTE: Given the large number of airports and the size of the circles if may be
necessary to zoom in an are to help Tap tool identify the airport to select.

To run the script execute:

>> python airports_dashboard.py