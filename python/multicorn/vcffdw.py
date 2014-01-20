from multicorn import ForeignDataWrapper
import cyvcf
from cyvcf import utils
import glob, re

class vcfWrapper (ForeignDataWrapper):
  ''' parent class for other vcf wrappers '''

  def __init__(self, options, columns):
    super(vcfWrapper, self).__init__(options, columns)
    self.columns = columns
    self.readers = {}

    directory = options.get('directory', None)
    if directory is not None:
      self.setup_vcf(directory)

  def setup_vcf (self, directory):
    self.readers = {} 
    for vcf_file in glob.glob(directory):
      if vcf_file is not None:
        try:
          self.readers[vcf_file] = cyvcf.Reader(filename=vcf_file)
        except:
          raise Exception("Can not open vcf file: " + vcf_file)
    
  def reset_samples (self):
    for reader in self.readers.values():
      reader.reset_samples()
    return (self.samples())

  def subset_by_samples (self, samples):
    for reader in self.readers.values():
      reader.subset_by_samples(samples)

  def samples(self):
    all_samples = set()
    for reader in self.readers.values():
      all_samples = all_samples.union(reader.samples)
    return list(all_samples)

class genotypeFdw (ForeignDataWrapper):
  def __init__(self, options, columns):
    super(genotypeFdw, self).__init__(options, columns)
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

class gtWideFdw (vcfWrapper):
  ''' return vcf in a wide format
      only accept a single VCF
  '''
  def __init__(self, options, columns):
    super(gtWideFdw, self).__init__(options, columns)

  def execute(self, quals, columns):
    begin = None
    stop = None
    chrom = None
    qsample = None
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
        qsample = qual.value
      elif qual.field_name == 'filter':
        filter = qual.value
      elif qual.field_name == 'directory':
        directory = qual.value

    ''' allow update vcf files other than those used in options duringtable definition '''
    if directory is not None:
      self.setup_vcf(directory)

    if len(self.readers) == 0:
      raise Exception("No VCF file is opened.")

    if (chrom is None or begin is None or stop is None):
      raise Exception("chrom, begin and stop need to be specified")

    ''' Select samples to be returned, not clear if it would improve speed in some situations '''
    all_samples = self.reset_samples()

    if (qsample is None):
      wanted_sample = all_samples
    elif (type(qsample) != list):
      wanted_sample = re.split('\|', qsample)
    else:
      raise Exception("query 'sample in (a,b,c)' is not implemented. Use sample='a|b|c' instead.")

    wanted_sample = [s for s in wanted_sample if s in columns]

    if (len(wanted_sample) != len(all_samples)):
      self.subset_by_samples(wanted_sample)
      
    line = { 'directory' : directory,
             'begin' : begin,
             'stop' : stop,
             'sample' : qsample,
    }

    for vcf_file, curr_reader in self.readers.items():
      line['file'] = vcf_file
      if len(wanted_sample) > 0 and len(curr_reader.samples) == 0:
        continue
      for record in curr_reader.fetch(chrom, begin, stop):
        line['chrom'] = record.CHROM
        line['pos'] = record.POS
        line['id'] = record.ID
        line['ref'] = record.REF
        line['alt'] = record.ALT
        line['qual'] = record.QUAL
        line['filter'] = record.FILTER
        line['format'] = record.FORMAT
        line['info'] = record.INFO
        for s in curr_reader.samples:
          line[s] = record.genotype(s)['GT']
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


class infoFdw (ForeignDataWrapper):
  ''' Wrapper only returns variation information.
      No genotypes will be passed '''
  
  def __init__(self, options, columns):
    super(infoFdw, self).__init__(options, columns)
    self.columns = columns

  def execute(self, quals, columns):
    begin = None
    stop = None
    chrom = None
    filter = None
    directory = None
    for qual in quals:
      if qual.field_name == 'begin':
        begin = qual.value
      elif qual.field_name == 'stop':
        stop = qual.value
      elif qual.field_name == 'chrom':
        chrom = qual.value
      elif qual.field_name == 'filter':
        filter = qual.value
      elif qual.field_name == 'directory':
        directory = qual.value

    if (directory is not None and chrom is not None and begin is not None and stop is not None):
      for vcf_file in glob.glob(directory):
        try:
          reader = cyvcf.Reader(filename=vcf_file)
          reader.subset_by_samples([])
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
          yield line
