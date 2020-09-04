# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida-core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
"""Tests for the :mod:`aiida.engine.daemon.execmanager` module."""
import os
import pytest

#from aiida import orm
from aiida.engine.daemon import execmanager
from aiida.transports.plugins.local import LocalTransport


@pytest.mark.usefixtures('clear_database_before_test')
def test_retrieve_files_from_list(tmp_path_factory, generate_calculation_node):
    """Test the `retrieve_files_from_list` function."""
    node = generate_calculation_node()

    retrieve_list = [
        'file_a.txt',
        ('sub/folder', 'sub/folder', 0),
    ]

    source = tmp_path_factory.mktemp('source')
    target = tmp_path_factory.mktemp('target')

    content_a = b'content_a'
    content_b = b'content_b'

    with open(str(source / 'file_a.txt'), 'wb') as handle:
        handle.write(content_a)
        handle.flush()

    os.makedirs(str(source / 'sub' / 'folder'))

    with open(str(source / 'sub' / 'folder' / 'file_b.txt'), 'wb') as handle:
        handle.write(content_b)
        handle.flush()

    with LocalTransport() as transport:
        transport.chdir(str(source))
        execmanager.retrieve_files_from_list(node, transport, str(target), retrieve_list)

    assert sorted(os.listdir(str(target))) == sorted(['file_a.txt', 'sub'])
    assert os.listdir(str(target / 'sub')) == ['folder']
    assert os.listdir(str(target / 'sub' / 'folder')) == ['file_b.txt']

    with open(str(target / 'sub' / 'folder' / 'file_b.txt'), 'rb') as handle:
        assert handle.read() == content_b

    with open(str(target / 'file_a.txt'), 'rb') as handle:
        assert handle.read() == content_a


#@pytest.mark.usefixtures('clear_database_before_test')
#def test_upload_calculation(tmp_path_factory, generate_calc_job, aiida_localhost):
#    """Test the `upload_calculation` method."""
#    from aiida.common.folders import Folder
#    from aiida.common.datastructures import CalcInfo, CodeInfo
#
#    code_node = orm.Code(remote_computer_exec=(aiida_localhost, '/bin/bash')).store()
#    source = tmp_path_factory.mktemp('source')
#    target = tmp_path_factory.mktemp('target')
#    localf = tmp_path_factory.mktemp('localf')
#
#    metadata = {'options': {'resources': {'num_machines': 1, 'tot_num_mpiprocs': 1}}}
#
#    calc_node = generate_calc_job(
#       folder=localf,
#       entry_point_name='templatereplacer',
#       inputs={'metadata': metadata, 'code': code_node}
#    )
#    calc_node.computer = aiida_localhost
#    code_info = CodeInfo()
#    code_info.code_uuid = code_node.uuid
#    calc_info = CalcInfo()
#    calc_info.uuid = str(code_node.uuid)
#    calc_info.codes_info = [code_info]
#    local_folder = Folder(abspath=str(source))
#
#    with LocalTransport() as transport:
#        transport.chdir(str(target))
#        execmanager.upload_calculation(node=calc_node, transport=transport, calc_info=calc_info, folder=local_folder)
