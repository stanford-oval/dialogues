# Copyright 2022 The Board of Trustees of the Leland Stanford Junior University
#
# Author: Mehrad Moradshahi <mehrad@cs.stanford.edu>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dialogues',
    version='0.0.2',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['dialogues=dialogues.__main__:main'],
    },
    package_data={
        'dialogues': [
            'bitod/src/knowledgebase/apis/*.json',
            'bitod/src/knowledgebase/dbs/*.json',
            'bitod/src/knowledgebase/mappings/*.json',
            'bitod/src/knowledgebase/mappings/*.dot',
            'bitod/src/templates/files/*/*',
        ]
    },
    license='BSD-3-Clause',
    author="Mehrad Moradshahi",
    author_email="mehrad@cs.stanford.edu",
    description="This package provides a unified interface to several dialogue benchmarks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mehrad0711/dialogues",
    install_requires=['pydot==1.4.2', 'pymongo==3.11.2', 'dnspython==2.1.0', 'word2number==1.1', 'dictdiffer~=0.9'],
)
