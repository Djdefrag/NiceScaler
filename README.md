<div align="center">
    <br>
    <img src="https://github.com/Djdefrag/NiceScaler/blob/main/logo.png" width="175"> </a> 
    <br><br> Image/Video Deeplearning Upscaler App for Windows <br><br>
    <a href="https://github.com/Djdefrag/NiceScaler/releases">
         <img src="https://user-images.githubusercontent.com/86362423/162710522-c40c4f39-a6b9-48bc-84bc-1c6b78319f01.png" width="200">
    </a>
</div>
<br>
<div align="center">
    <img src="https://user-images.githubusercontent.com/32263112/185062867-1e725e1d-b0a8-46ed-aa48-fd15041dfb34.png"> </a> 
</div>

## Credits.
ESPCN   (https://arxiv.org/pdf/1609.05158.pdf)

FSRCNN  (https://arxiv.org/pdf/1608.00367.pdf)

LapSRN  (https://arxiv.org/pdf/1710.01992.pdf)

## How is made.
NiceScaler is completely written in Python, from backend to frontend. External packages are:
- [ ] AI  -> OpenCV
- [ ] GUI -> Tkinter / Tkdnd / Sv_ttk
- [ ] Image/video -> OpenCV / Moviepy
- [ ] Packaging   -> Pyinstaller
- [ ] Miscellaneous -> Pywin32 / Win32mica / Image_slicer

## Installation.
1) download the release
2) execute NiceScaler.exe

## Requirements
- [ ] Windows 11 / Windows 10
- [ ] RAM >= 8Gb
- [ ] Directx12 compatible GPU:
    - [ ] any AMD >= Radeon HD 7000 series
    - [ ] any Intel HD Integrated >= 4th-gen core
    - [ ] any NVIDIA >=  GTX 600 series
- [ ] CPU

## Features.
- [x] Easy to use GUI
- [x] Image/list of images upscale
- [x] Video upscale
- [x] Drag&drop files [image/multiple images/video]
- [x] Different upscale factors:
    - [x] x2   - 500x500px -> 1000x1000px
    - [x] x4   - 500x500px -> 2000x2000px
- [x] Cpu and Gpu backend
- [x] Compatible images - png, jpeg, bmp, webp, tif  
- [x] Compatible video  - mp4, wemb, gif, mkv, flv, avi, mov, qt 

## Next steps.
- [x] New GUI with Windows 11 style
- [ ] Include audio for upscaled video
- [ ] Update libraries 
    - [ ] Python 3.10 (expecting ~10% more performance) 
    - [ ] Python 3.11 (expecting ~30% more performance, now in beta)

## Known bugs.
- [ ] Filenames with non-latin symbols (for example kangy, cyrillic etc.) not supported - [Temp solution] rename files like "image" or "video"

## Example. 

Original photo

![rPc+73](https://user-images.githubusercontent.com/32263112/155835499-fef341fb-d727-40f6-841c-5c41a1340499.png)

Upscaled photo

![testx4ddd](https://user-images.githubusercontent.com/32263112/157822217-9742b155-fe63-41a8-b057-81c833719b1d.png)


 
