<a name="readme-top"></a>

<!-- Presentation Block -->
<br />

<div align="center">

  <a href="https://github.com/LightDestory/MultiProcessImageProcessingBench">
    <img src="https://raw.githubusercontent.com/LightDestory/MultiProcessImageProcessingBench/master/.github/assets/images/presentation_image.gif" alt="Preview" width="90%">
  </a>

  <h2 align="center">MultiProcess Image Processing Bench</h2>
  
  <p align="center">
      A tool designed for benchmarking parallelizable image processing algorithms using Python and the multiprocessing module
  </p>
  
  <br />
  <br />

</div>

<!-- ToC -->

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#book-about-the-project">📖 About The Project</a>
    </li>
    <li>
      <a href="#gear-getting-started">⚙️ Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#warning-license">⚠️ License</a></li>
    <li><a href="#hammer_and_wrench-built-with">🛠️ Built With</a></li>
  </ol>
</details>

<!-- About Block -->

## :book: About The Project

MultiProcess Image Processing is a tool designed for benchmarking parallelizable image processing algorithms using Python and the multiprocessing module. This tool enables users to assess the performance and efficiency of different image processing techniques when executed in parallel on multiple cores.

The tool provides a user-friendly interface that allows users to input their image, select a processing algorithm and specify the desired number of processes to be utilized. It then automatically divides the image data into manageable chunks and assigns them to separate processes for parallel execution.

The tool is written in Python and uses the multiprocessing module to parallelize the execution of the image processing algorithms. It also uses the Matplotlib library to display the results and the CustomTkinter library to create the user interface.

_This tool was developed as part of a final project for the course "Multimedia" at the University of Study of Catania, Department of Mathematics and Computer Science._

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Setup Block -->

## :gear: Getting Started

It is compatible with Windows, Linux and MacOS. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Prerequisites

This tool requires Python 3.9 or higher to run. You can download the latest version of Python [here](https://www.python.org/downloads/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation

First of all, clone the repository anywhere on your pc:

      git clone https://github.com/LightDestory/MultiProcessImageProcessingBench

Now, to install this tool you need to install the dependencies:

- Install the requirements using `pip` (create a `venv` if you want):

      `pip install -r requirements.txt`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Usage

You can run the tool by executing the `main.py` file:

      python main.py

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- License Block -->

## :warning: License

The content of this repository is distributed under the GNU GPL-3.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- Built With Block -->

## :hammer_and_wrench: Built With

- [Python](https://www.python.org/)
- [Multiprocessing module](https://docs.python.org/3/library/multiprocessing.html#module-multiprocessing)
- [Matplotlib](https://matplotlib.org/)
- [CustomTkinter](https://customtkinter.tomschimansky.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>
