# Cross-correlation Analysis Tool

This is a tool I developed to analyze the data from my PhD thesis project. In short, it uses the [cross-correlation function](https://en.wikipedia.org/wiki/Cross-correlation) (CCF) between an observed spectrum of a star and a theoretical model spectrum of the star. The CCF is essentially a template-matching algorithm, and has a strong peak when the template (the model spectrum) matches the observation (the real spectrum). I further constrain the properties of the star by generating several cross-correlation functions for models with different temperatures, rotational speeds (vsini), and metal enrichment factors ([Fe/H]). There is a bit more information about my project and this tool [here](http://www.as.utexas.edu/~kgulliks/Continuum_Talk#/).

This bokeh tool combines all of the cross-correlation functions I have generated into an easy to use dashboard. The top panel shows the maximum CCF height as a function of temperature. You can click on the individual points to update the CCF plot (lower left). The lower right plot shows the rotational speed and metal enrichment grid that I used; you can select parts of that to update the top plot and the CCF plot. Finally, there are two Select boxes that allow you to select different stars in my sample, as well as different instrument/date combinations when the star was observed multiple times. 

## Running the Tool.

To run this example, you first need to download the data. You can do this by typing the command

```python
python fetch_data.py
```

This tool runs through bokeh-server, so you can instantiate it with whatever your favorite options are. I included a shell script with the options that I generally use:

```bash
./run_ccf_server
```

The first thing it does is read in the HDF5 files with the CCF data, which will take about a minute. After that, the app should be responsive and update all plots within a second or so.


