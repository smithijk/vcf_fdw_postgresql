from multicorn import ForeignDataWrapper
import cyvcf
from cyvcf import utils
import glob

class vcfFdw (ForeignDataWrapper):
  def __init__(self, options, columns):
    super(vcfFdw, self).__init__(options, columns)
    self.columns = columns

  def execute(self, quals, columns):
    begin = None
    stop = None
    chrom = None
    sample = None
    filter = None
    directory = None
    for qual in quals:
      if qual.field_name == 'begin':
        begin = qual.value
      elif qual.field_name == 'stop':
        stop = qual.value
      elif qual.field_name == 'chrom':
        chrom = qual.value
      elif qual.field_name == 'sample':
        sample = qual.value
      elif qual.field_name == 'filter':
        filter = qual.value
      elif qual.field_name == 'directory':
        directory = qual.value

    if (sample is None):
      wanted_sample = []
    elif (type(sample) != list):
      wanted_sample = [sample]
    else:
      wanted_sample = sample

    if (directory is not None and chrom is not None and begin is not None and stop is not None):
      for vcf_file in glob.glob(directory):
        try:
          reader = cyvcf.Reader(filename=vcf_file)
          if (sample is not None):
            reader.subset_by_samples(wanted_sample)
        except:
          continue
        for record in reader.fetch(chrom, begin, stop):
          line = {}
          line['file'] = vcf_file
          line['begin'] = begin
          line['stop'] = stop
          line['chrom'] = chrom
          line['chrom'] = record.CHROM
          line['pos'] = record.POS
          line['id'] = record.ID
          line['ref'] = record.REF
          line['alt'] = record.ALT
          line['qual'] = record.QUAL
          line['filter'] = record.FILTER
          line['format'] = record.FORMAT
          line['info'] = record.INFO
          line['directory'] = directory
          for s in reader.samples:
            line['sample'] = s
            line['genotype'] = record.genotype(s)['GT']
            yield line
   
class sampleFdw (ForeignDataWrapper):
  def __init__(self, options, columns):
    super(sampleFdw, self).__init__(options, columns)
    self.columns = columns

  def execute(self, quals, columns):
    directory = None
    for qual in quals:
      if qual.field_name == 'directory':
        directory = qual.value

    if (directory is not None):
      for vcf_file in glob.glob(directory):
        try:
          reader = cyvcf.Reader(filename=vcf_file)
        except:
          continue
        for s in reader.samples:
          line = {}
          line['sample'] = s
          line['file'] = vcf_file
          line['directory'] = directory
          yield line
