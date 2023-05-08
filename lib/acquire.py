import time
import fp
from org.lsst.ccs.utilities.location import LocationSet
import ucd_bench
import ucd_stage

class TestCoordinator(object):
    """Base class for taking images.

    Parameters
    ----------
    options : `dict`
       Dictionary contining image acquisition options.
    test_type : `str`
       Type of acquisition test.
    image_type : `str`
       Type of image.
    """

    def __init__(self, options, test_type, image_type):
        self.run = options['run']
        self.test_type = test_type
        self.image_type = image_type
        self.annotation = options.get('annotation', '')
        self.locations = LocationSet(options.get('locations', ''))
        self.clears = options.getInt('clears', 1)
        self.extra_delay = options.getFloat('extradelay', 0)

    def take_images(self):
        raise NotImplementedError

    def take_bias_images(self, count):
        """Take multiple bias images.

        Parameters
        ----------
        count : `int`
            Number of bias images to take.
        """
        for i in range(count):
            self.take_bias_image()

    def create_fits_header_data(self, exposure, image_type):
        """Create a dictionary of FITS header keyword names and values.

        Parameters
        ----------
        exposure : `float`
            Exposure time in seconds.
        image_type : `str`
            Description of the image type.

        Returns
        -------
        data : `dict`
            Dictionary of FITS header keyword names and values.
        """
        data = {'ExposureTime' : exposure, 
                'TestType' : self.test_type,
                'ImageType' : image_type}

        if self.run:
            data.update({'RunNumber' : self.run})

        return data

    def take_bias_image(self):
        """Take a bias image."""
        return self.__take_image(0, None, image_type='BIAS')

    def take_image(self, exposure, expose_command, image_type=None):
        """Take a test image."""
        return self.__take_image(exposure, expose_command, image_type)

    def __take_image(self, exposure, expose_command, image_type=None):
        """Base method for taking an image.

        Parameters
        ----------
        exposure : `float`
            Exposure time in seconds.
        expose_command : `function`
            A callable that defines the exposure.
        image_type : `str`
            Description of the image type.
        """
        image_type = image_type if image_type else self.image_type

        if self.extra_delay > 0:
            print "Extra delay %g" % self.extra_delay
            time.sleep(self.extra_delay)

        fits_header_data = self.create_fits_header_data(exposure, image_type)
        file_list = fp.takeExposure(expose_command, fits_header_data, self.annotation, self.locations, self.clears)

        return file_list

class BiasTestCoordinator(TestCoordinator):
    """A TestCoordinator for taking only bias images."""

    def __init__(self, options):
        super(BiasTestCoordinator, self).__init__(options, 'BIAS', 'BIAS')
        self.count = options.getInt('count', 10)

    def take_images(self):
        """Take multiple bias images."""
        self.take_bias_images(self.count)

class BiasPlusImagesTestCoordinator(TestCoordinator):
    """Base Class for all tests that involve n bias images per test image."""

    def __init__(self, options, test_type, image_type):
        super(BiasPlusImagesTestCoordinator, self).__init__(options, test_type, image_type)
        self.bcount = int(options.get('bcount', '1'))

    def take_bias_plus_image(self, exposure, expose_command, image_type=None):
        """Take a bias image and a test image."""
        self.take_bias_images(self.bcount)
        self.take_image(exposure, expose_command, image_type)

class DarkTestCoordinator(BiasPlusImagesTestCoordinator):
    """A TestCoordinator for darks."""

    def __init__(self, options):
        super(DarkTestCoordinator, self).__init__(options, 'DARK', 'DARK')
        self.darks = options.getList('dark')

    def take_images(self):
        """Take multiple dark images."""
        for dark in self.darks:
            integration, count = dark.split()
            integration = float(integration)
            count = int(count)
            expose_command = lambda: time.sleep(integration)

            for c in range(count):
                self.take_bias_plus_image(integration, expose_command)

class FlatFieldTestCoordinator(BiasPlusImagesTestCoordinator):
    """A TestCoordinator for flats."""

    def __init__(self, options):
        super(FlatFieldTestCoordinator, self).__init__(options, 'FLAT', 'FLAT')
        self.flats = options.getList('flat')
        self.wl_filter = options.get('wl')
        self.hilim = options.getFloat('hilim', 999.0)
        self.lolim = options.getFloat('lolim', 1.0)
        self.signalpersec = float(options.get('signalpersec'))

    def take_images(self):
        """Take multiple flat field images."""
        for flat in self.flats:
            e_per_pixel, count = flat.split()
            e_per_pixel = float(e_per_pixel)
            exposure = self.compute_exposure_time(e_per_pixel)
            count = int(count)
            expose_command = lambda : ucd_bench.openShutter(exposure)

            for c in range(count):
                self.take_bias_plus_image(exposure, expose_command)

    def compute_exposure_time(self, e_per_pixel):
        e_per_pixel = float(e_per_pixel)
        seconds = np.round(e_per_pixel/self.signalpersec, 1)
        if seconds>self.hilim:
           print "Warning: exposure time %g > hilim (%g)" % (seconds, self.hilim)
           seconds = self.hilim
        if seconds<self.lolim:
           print "Warning: exposure time %g < lolim (%g)" % (seconds, self.lolim)
           seconds = self.lolim
        print "Computed Exposure %g for e_per_pixel=%g" % (seconds, e_per_pixel)
        return seconds

class PersistenceTestCoordinator(BiasPlusImagesTestCoordinator):
    ''' A TestCoordinator for all tests that involve taking persitence with the flat field generator '''
    def __init__(self, options):
        super(PersistenceTestCoordinator, self).__init__(options, "BOT_PERSISTENCE", "FLAT")
        self.bcount = options.getInt('bcount', 10)
        self.wl_filter = options.get('wl')
        self.signalpersec = float(options.get('signalpersec'))
        self.persistence= options.getList('persistence')

    def take_images(self):
        e_per_pixel, n_of_dark, exp_of_dark, t_btw_darks= self.persistence[0].split()
        e_per_pixel = float(e_per_pixel)
        exposure = self.compute_exposure_time(e_per_pixel)

        # bias acquisitions
        self.take_bias_images(self.bcount)

        # dark acquisition
        expose_command = lambda: ucd_bench.openShutter(exposure)
        file_list = super(PersistenceTestCoordinator, self).take_image(exposure, expose_command, "FLAT")

        # dark acquisition
        for i in range(int(n_of_dark)):
            time.sleep(float(t_btw_darks))
            super(PersistenceTestCoordinator, self).take_image(float(exp_of_dark), lambda: time.sleep(float(exp_of_dark)), image_type="DARK")
        return file_list

    def compute_exposure_time(self, e_per_pixel):
        e_per_pixel = float(e_per_pixel)
        seconds = np.round(e_per_pixel/self.signalpersec, 1)
        print "Computed Exposure %g for e_per_pixel=%g" % (seconds, e_per_pixel)
        return seconds

class SpotTestCoordinator(BiasPlusImagesTestCoordinator):
    """A TestCoordinator for spot/streak images."""

    def __init__(self, options):
        super(SpotTestCoordinator, self).__init__(options, 'SPOT', 'SPOT')
        self.imcount = int(options.get('imcount', '1'))
        self.mask = options.get('mask')
        self.exposures = options.getList('expose')
        self.points = options.getList('point')
        self.stagex = 0
        self.stagey = 0
        self.stagez = 0

    def take_images(self):
        """Take multiple spot images."""
        def moveTo(point):
            """A wrapper to 'moveTo' to store the current position."""
            splittedpoints = point.split()
            x = float(splittedpoints[0])
            y = float(splittedpoints[1])
            z = float(splittedpoints[2])
            if self.stagex == x and self.stagey == y and self.stagez == z:
                return
            else:
                ucd_stage.moveTo(x, y, z)
                self.stagex = x
                self.stagey = y
                self.stagez = z

        for point in self.points:
            moveTo(point)

            for exposure in self.exposures:
                exposure = float(exposure)
                expose_command = lambda: ucd_bench.openShutter(exposure)
                for i in range(self.imcount):
                    self.take_bias_plus_image(exposure, expose_command)

def do_bias(options):
    """Initialize a BiasTestCoordinator and take images."""
    print "bias called {0}".format(options)
    tc = BiasTestCoordinator(options)
    tc.take_images()

def do_dark(options):
    """Initialize a DarkTestCoodrinator and take images."""
    print "dark called {0}".format(options)
    tc = DarkTestCoordinator(options)
    tc.take_images()

def do_flat(options):
    """Initialize a FlatFieldTestCoordinator and take images."""
    print "flat called {0}".format(options)
    tc = FlatFieldTestCoordinator(options)
    tc.take_images()
   
def do_persistence(options):
    """Initialize a PersistenceTestCoordinator and take images."""
    print "Persistence called %s" % options
    tc = PersistenceTestCoordinator(options)
    tc.take_images()

def do_spot(options):
    """Initialize a SpotTestCoordinator and take images."""
    print "spot called {0}".format(options)
    tc = SpotTestCoordinator(options)
    tc.take_images()
