# No Imports Allowed!

def Reverse(lst): 
    #helper function that reverses a list
    return [ele for ele in reversed(lst)] 

def backwards(sound):
   #creates a new dictionary by reversing left and right, using above helper function 
    d = {'rate' : sound["rate"], 'left' : Reverse(sound['left']),
         'right' : Reverse(sound['right'])}
    return(d) 
    

def mix(sound1, sound2, p):
    #check if sounds have the same rate
    if sound1['rate'] == sound2['rate']:
        #create new lists for left and right
        new_sound_left = []
        new_sound_right = []
        #sound length is dependent on shorter of the two
        base_sound = min(len(sound1['left']), len(sound2['left']))
        #multiply entries of each list accordingly
        for i in range(base_sound): 
            new_sound_left.append(p*sound1['left'][i] + (1-p)*sound2['left'][i])
            new_sound_right.append(p*sound1['right'][i] + (1-p)*sound2['right'][i])
        #return final sound
        final_sound = {'rate' : sound1['rate'], 'left' : new_sound_left, 'right' : new_sound_right}
        return final_sound
    else:
     return None

def MultiplyList(sound, scale):
    #helper function that multiplies entries in a list by scale
    sound_copy = sound.copy()
    for i in range(len(sound)):
        sound_copy[i] = sound_copy[i]*scale
    return sound_copy

def AddLists(list1, list2):
    #helper function that adds entries of two lists
    for i in range(len(list1)):
        list2[i] = list2[i]+list1[i]

def echo(sound, num_echos, delay, scale):
    #obtain lists of left and right sound data
    sound_left = sound['left']
    sound_right = sound['right']
    #calculate delay and extension
    sample_delay = round(delay*sound['rate'])
    extension = num_echos*sample_delay
    #initializes sound lists 
    sound_left_final = [0]*(len(sound_left)+extension)
    sound_right_final = [0]*(len(sound_right)+extension)
    #loop through to each echo
    for i in range(num_echos+1):
        #pad each new list with zeros accordingly
        a = i*sample_delay*[0]+MultiplyList(sound_left,scale**(i))+(extension-sample_delay*i)*[0]
        b = i*sample_delay*[0]+MultiplyList(sound_right,scale**(i))+(extension-sample_delay*i)*[0]
        #cummulative lists 
        AddLists(a, sound_left_final)
        AddLists(b, sound_right_final) 
    #create the final sound
    final_sound =  {'rate' : sound['rate'], 'left' : sound_left_final, 'right' : sound_right_final}
    return final_sound 
            

def pan(sound):
    #create copies of right and left
    sound_right_copy = sound['right'].copy()
    sound_left_copy = sound['left'].copy()
    #store length as a variable
    sample_length = len(sound_right_copy)
    count = 0
    #compute calculations for left and right
    for i in range(sample_length):
        sound_right_copy[i] = sound_right_copy[i]*(count/(sample_length-1))
        sound_left_copy[i] = sound_left_copy[i]*(1-(count/(sample_length-1)))
        count += 1
    #create new dictionary
    new_dictionary = {'rate': sound['rate'], 'left': sound_left_copy, 'right': sound_right_copy}
    return(new_dictionary)       
        
def remove_vocals(sound):
    #create copies of left and right
    sound_right_copy = sound['right'].copy()
    sound_left_copy = sound['left'].copy()
    #store length as a variable
    sample_length = len(sound_right_copy)
    #compute calculations for left and right 
    for i in range(sample_length):
        a = sound_right_copy[i]
        b = sound_left_copy[i]
        sound_right_copy[i] = b-a
        sound_left_copy[i] = b-a
    #create new dictionary
    new_dictionary = {'rate': sound['rate'], 'left': sound_left_copy, 'right': sound_right_copy}
    return(new_dictionary)


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    #code in this block will only be run when you explicitly run your script,
    #and not when the tests are being run.  this is a good place to put your
    #code for generating and saving sounds, or any other code you write for
    #testing, etc.

    #here is an example of loading a file (note that this is specified as
    #sounds/hello.wav, rather than just as hello.wav, to account for the
    #sound files being in a different directory than this file)
    
    hello = load_wav('sounds/hello.wav')
    write_wav(backwards(hello), 'hello_reversed.wav')
    
    mystery = load_wav('sounds/mystery.wav')
    write_wav(backwards(mystery), 'mystery_reversed.wav')
    
    synth = load_wav('sounds/synth.wav')
    water = load_wav('sounds/water.wav')
    write_wav(mix(synth, water, 0.2), 'synth_water_mix.wav')
        
    chord = load_wav('sounds/chord.wav')
    write_wav(echo(chord, 5, 0.3, 0.6), 'echo_chord.wav')
    
    car = load_wav('sounds/car.wav')
    write_wav(pan(car), 'pan_car.wav')
    
    coffee = load_wav('sounds/coffee.wav')
    write_wav(remove_vocals(coffee), 'removed_coffee.wav')
    
    
