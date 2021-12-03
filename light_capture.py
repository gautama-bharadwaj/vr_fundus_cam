# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2021 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# Acquisition.py shows how to acquire images. It relies on
# information provided in the Enumeration example. Also, check out the
# ExceptionHandling and NodeMapInfo examples if you haven't already.
# ExceptionHandling shows the handling of standard and Spinnaker exceptions
# while NodeMapInfo explores retrieving information from various node types.
#
# This example touches on the preparation and cleanup of a camera just before
# and just after the acquisition of images. Image retrieval and conversion,
# grabbing image data, and saving images are all covered as well.
#
# Once comfortable with Acquisition, we suggest checking out
# AcquisitionMultipleCamera, NodeMapCallback, or SaveToAvi.
# AcquisitionMultipleCamera demonstrates simultaneously acquiring images from
# a number of cameras, NodeMapCallback serves as a good introduction to
# programming with callbacks and events, and SaveToAvi exhibits video creation.

import os
import PySpin
import sys
from PIL import Image
import serial
import time

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=.1)

NUM_IMAGES =5  # number of images to grab


def acquire_images(cam, nodemap, nodemap_tldevice):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True
        # Set acquisition mode to acquire a single frame, this ensures acquired images are sync'd since camera 2 and 3 are setup to be triggered
        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)

        print('Acquisition mode set to single frame...')

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)


        # Retrieve, convert, and save images
        for i in range(NUM_IMAGES):
            try:

                #  Retrieve next received image
                #
                #  *** NOTES ***
                #  Capturing an image houses images on the camera buffer. Trying
                #  to capture an image that does not exist will hang the camera.
                #
                #  *** LATER ***
                #  Once an image from the buffer is saved and/or no longer
                #  needed, the image must be released in order to keep the
                #  buffer from filling up.

                print(i)
                time.sleep(0.2)
                arduino.write(bytes(str(i), 'utf-8'))
                #  Begin acquiring images
                #
                #  *** NOTES ***
                #  What happens when the camera begins acquiring images depends on the
                #  acquisition mode. Single frame captures only a single image, multi
                #  frame catures a set number of images, and continuous captures a
                #  continuous stream of images. Because the example calls for the
                #  retrieval of 10 images, continuous mode has been set.
                #
                #  *** LATER ***
                #  Image acquisition must be ended when no more images are needed.
                cam.BeginAcquisition()

                image_result = cam.GetNextImage()

                #  Ensure image completion
                #
                #  *** NOTES ***
                #  Images can easily be checked for completion. This should be
                #  done whenever a complete image is expected or required.
                #  Further, check image status for a little more insight into
                #  why an image is incomplete.
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:
                    #  Print image information; height and width recorded in pixels
                    #
                    #  *** NOTES ***
                    #  Images have quite a bit of available metadata including
                    #  things such as CRC, image status, and offset values, to
                    #  name a few.
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    #  Convert image to mono 8
                    #
                    #  *** NOTES ***
                    #  Images can be converted between pixel formats by using
                    #  the appropriate enumeration value. Unlike the original
                    #  image, the converted one does not need to be released as
                    #  it does not affect the camera buffer.
                    #
                    #  When converting images, color processing algorithm is an
                    #  optional parameter.
                    image_converted = image_result.Convert(PySpin.PixelFormat_RGB8, PySpin.HQ_LINEAR)

                    # Create a unique filename
                    if device_serial_number:
                        filename = 'Acquisition-%s-%d.jpg' % (device_serial_number, i)
                    else:  # if serial number is empty
                        filename = 'Acquisition-%d.jpg' % i

                    #  Save image
                    #
                    #  *** NOTES ***
                    #  The standard practice of the examples is to use device
                    #  serial numbers to keep images of one device from
                    #  overwriting those of another.
                    print(type(image_converted))
                    image_converted.Save(filename)
                    print('Image saved at %s' % filename)

                    #  Release image
                    #
                    #  *** NOTES ***
                    #  Images retrieved directly from the camera (i.e. non-converted
                    #  images) need to be released in order to keep from filling the
                    #  buffer.
                    # image_result.Release()  
                    # End acquisition
                    #
                    #  *** NOTES ***
                    #  Ending acquisition appropriately helps ensure that devices clean up
                    #  properly and do not need to be power-cycled to maintain integrity.
                    cam.EndAcquisition()

                    # To re-size the image
                    # baseheight = 560
                    # img = Image.open(filename)
                    # hpercent = (baseheight / float(img.size[1]))
                    # wsize = int((float(img.size[0])))
                    # img = img.resize((wsize, baseheight), Image.ANTIALIAS)
                    # img.save('resized_image.jpg')
                    print('')

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    # Initializing Arduino serial input
    print('Initializing Arduino serial connection...')
    arduino.write(bytes('-1', 'utf-8'))
    time.sleep(1)

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:

        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):

        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        # time.sleep(5)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    return result

if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
