"""
    A simple script to be called from the main script when creating graphs with translated values
    Currently only used for conversions between frequency and wavelength
    1/27/2025 Resbi & RJGamesAhoy
"""

SPEED_OF_LIGHT = 2.99792458e8 # Speed of light in M/s

class RadioConversions():

    # default converisons are from MHZ -> CM and CM -> MHZ

    def frequencyToWavelength(self, frequency, units = 'mhz', outUnits = 'cm'):
        match units:
            case 'hz':
                frequencyInHertz = frequency
            case 'mhz':
                frequencyInHertz = self.mhzToHertz(frequency)
        
        wavelength = SPEED_OF_LIGHT / frequencyInHertz

        match outUnits:
            case 'm':
                pass
            case 'cm':
                wavelength = self.meterToCentimeter(wavelength)
    
        return wavelength
    def wavelengthToFrequency(self, wavelength, units = 'cm', outUnits = 'mhz'):
        match units:
            case 'cm':
                wavelengthInMeters = self.centimeterToMeter(wavelength)
            case 'm':
                wavelengthInMeters = wavelength

        frequency = SPEED_OF_LIGHT / wavelengthInMeters 

        match outUnits:
            case 'hz':
                pass
            case 'mhz':
                frequency = self.hertzToMhz(frequency)
        return frequency
    
    def mhzToHertz(self, frequencyInMhz):
        frequencyInHz = frequencyInMhz * 10e5
        return frequencyInHz
    
    def hertzToMhz(self, frequencyInHertz):
        frequencyInMegahertz = frequencyInHertz / 10e5
        return frequencyInMegahertz
    
    def meterToCentimeter(self, wavelengthInMeters):
        wavelengthInCentimeters = wavelengthInMeters * 100
        return wavelengthInCentimeters
    
    def centimeterToMeter(self, wavelengthInCentimeters):
        wavelengthInMeters = wavelengthInCentimeters / 100
        return wavelengthInMeters

    
unitConverter = RadioConversions()
test = unitConverter.frequencyToWavelength(1420.05)

print(test)
