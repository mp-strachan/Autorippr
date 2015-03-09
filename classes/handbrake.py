"""
HandBrake CLI Wrapper


Released under the MIT license
Copyright (c) 2012, Jason Millward

@category   misc
@version    $Id: 1.6.2, 2014-12-03 20:12:25 ACDT $;
@author     Jason Millward <jason@jcode.me>
@license    http://opensource.org/licenses/MIT
"""

import os
import subprocess
import logger

class HandBrake(object):

    def __init__(self, debug, compressionpath):
        self.log = logger.Logger("HandBrake", debug)
        self.compressionPath = compressionpath

    def compress(self, nice, args, dbmovie):
        """
            Passes the necessary parameters to HandBrake to start an encoding
            Assigns a nice value to allow give normal system tasks priority

            Inputs:
                nice    (Int): Priority to assign to task (nice value)
                args    (Str): All of the handbrake arguments taken from the
                                settings file
                output  (Str): File to log to. Used to see if the job completed
                                successfully

            Outputs:
                Bool    Was convertion successful
        """
        checks = 0

        moviename = "%s.mkv" % dbmovie.moviename
        inmovie = "%s/%s" % (dbmovie.path, dbmovie.filename)
        outmovie = "%s/%s" % (dbmovie.path, moviename)

        command = 'nice -n {0} {4}HandBrakeCLI --verbose -i "{1}" -o "{2}" {3}'.format(
            nice, 
            inmovie,
            outmovie,
            ' '.join(args),
            self.compressionPath
        )
 
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )
        (results, errors) = proc.communicate()

        if proc.returncode is not 0:
            self.log.error(
                "HandBrakeCLI (compress) returned status code: %d" % proc.returncode)

        if results is not None and len(results) is not 0:
            lines = results.split("\n")
            for line in lines:
                if "Encoding: task" not in line:
                    self.log.debug(line.strip())

                if "average encoding speed for job" in line:
                    checks += 1

                if "Encode done!" in line:
                    checks += 1

                if "ERROR" in line and "opening" not in line:
                    self.log.error(
                        "HandBrakeCLI encountered the following error: ")
                    self.log.error(line)

                    return False

        if checks >= 2:
            self.log.debug("HandBrakeCLI Completed successfully")

            return True
        else:
            return False
