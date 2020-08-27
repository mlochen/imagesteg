# imagesteg

This script hides a file inside an image. It uses the two least significant bits of the 8-bit color channels of an RGB image. So it can hide six bits per pixel and therefore roughly width*height*6/8 bytes in an image (a little bit less because of escape characters and the end mark). This creates a very slight noise in the resulting image, that is unrecognizable to the human eye. This works best if the original image is already noisy, so avoid using images with big areas of the same color.

## Example
This is a normal image:

![original](example/original.jpg)

Now let's hide some data inside:

    $ python imagesteg.py example/original.jpg example/primes.pdf 
    Encode data
    Password: steganography is cool
    Save as: modified.png
    $
    
The resulting image:

![modified](example/modified.png)

**Important: Only use lossless image formats like png or bitmap for the resulting image, otherwise the hidden data will be destroyed.**
Now let's recover the hidden data:

    $ python imagesteg.py modified.png 
    Decode data
    Password: steganography is cool 
    Save as: primes2.pdf
    $
    
primes2.pdf is the exact same file as primes.pdf. Of course this only works with the same password as used before.
