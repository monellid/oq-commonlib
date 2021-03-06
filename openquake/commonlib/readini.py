import ConfigParser
import csv
import os
from lxml import etree

from openquake import nrmllib
from openquake.commonlib.oqvalidation import OqParam


def _collect_source_model_paths(smlt):
    """
    Given a path to a source model logic tree or a file-like, collect all of
    the soft-linked path names to the source models it contains and return them
    as a uniquified list (no duplicates).
    """
    src_paths = []
    tree = etree.parse(smlt)
    for branch_set in tree.xpath('//nrml:logicTreeBranchSet',
                                 namespaces=nrmllib.PARSE_NS_MAP):

        if branch_set.get('uncertaintyType') == 'sourceModel':
            for branch in branch_set.xpath(
                    './nrml:logicTreeBranch/nrml:uncertaintyModel',
                    namespaces=nrmllib.PARSE_NS_MAP):
                src_paths.append(branch.text)
    return sorted(set(src_paths))


def parse_config(source, hazard_calculation_id=None, hazard_output_id=None):
    """
    Parse a dictionary of parameters from an INI-style config file.

    :param source:
        File-like object containing the config parameters.
    :param hazard_job_id:
        The ID of a previous calculation (or None)
    :param hazard_ouput_id:
        The output of a previous job (or None)
    :returns:
        An :class:`openquake.commonlib.oqvalidation.OqParam` instance
        containing the validate and casted parameters/values parsed from
        the job.ini file as well as a subdictionary 'inputs' containing
        absolute paths to all of the files referenced in the job.ini, keyed by
        the parameter name.
    """
    cp = ConfigParser.ConfigParser()
    cp.readfp(source)

    base_path = os.path.dirname(
        os.path.join(os.path.abspath('.'), source.name))
    params = dict(base_path=base_path, inputs={},
                  hazard_calculation_id=hazard_calculation_id,
                  hazard_output_id=hazard_output_id)

    # Directory containing the config file we're parsing.
    base_path = os.path.dirname(os.path.abspath(source.name))

    for sect in cp.sections():
        for key, value in cp.items(sect):
            if key == 'sites_csv':
                # Parse site coordinates from the csv file,
                # return a string 'lon1 lat1, lon2 lat2, ... , lonN latN'
                path = value if os.path.isabs(value) else os.path.join(
                    base_path, value)
                sites = open(path, 'U').read().strip().replace(',', ' ')
                params['sites'] = sites.replace('\n', ',')
            elif key.endswith('_file'):
                input_type = key[:-5]
                path = value if os.path.isabs(value) else os.path.join(
                    base_path, value)
                params['inputs'][input_type] = path
            else:
                params[key] = value

    # load source inputs (the paths are the source_model_logic_tree)
    smlt = params['inputs'].get('source_model_logic_tree')
    if smlt:
        params['inputs']['source'] = [
            os.path.join(base_path, src_path)
            for src_path in _collect_source_model_paths(smlt)]

    is_risk = hazard_calculation_id or hazard_output_id
    cmode = params['calculation_mode']
    if is_risk and cmode in ('classical', 'event_based', 'scenario'):
        raise ValueError('Please change calculation_mode=%s into %s_risk '
                         'in the .ini file' % (cmode, cmode))
    return OqParam(**params)
