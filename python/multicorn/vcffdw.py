from multicorn import ForeignDataWrapper
import cyvcf
from cyvcf import utils
import glob, re

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

class gtWideFdw (ForeignDataWrapper):
  ''' return vcf in a wide format
      only accept a single VCF
  '''
  def __init__(self, options, columns):
    super(gtWideFdw, self).__init__(options, columns)
    self.columns = columns

    self.vcf_file = options.get('vcf_file', None)
    if self.vcf_file is None:
      raise Exception("VCF file needs to be specified")
    try:
      self.reader = cyvcf.Reader(filename=self.vcf_file)
    except:
      raise Exception("Can not open vcf file: " + self.vcf_file)

  def execute(self, quals, columns):
    self.reader.reset_samples()

    begin = None
    stop = None
    chrom = None
    sample = None
    filter = None
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

    if (chrom is None or begin is None or stop is None):
      raise Exception("chrom, begin and stop need to be specified")

    ''' Not clear if below would gain anything '''
    if (sample is None):
      wanted_sample = self.reader.samples
    elif (type(sample) != list):
      wanted_sample = re.split('\|', sample)
    else:
      raise Exception("query 'sample in (a,b,c)' is not implemented. Use sample='a|b|c' instead.")

    wanted_sample = [s for s in wanted_sample if s in columns]

    if (len(wanted_sample) != len(self.reader.samples)):
      self.reader.subset_by_samples(wanted_sample)
      
    line = { 'file' : self.vcf_file,
             'begin' : begin,
             'stop' : stop,
             'sample' : sample,
    }
    
    for record in self.reader.fetch(chrom, begin, stop):
      line['chrom'] = record.CHROM
      line['pos'] = record.POS
      line['id'] = record.ID
      line['ref'] = record.REF
      line['alt'] = record.ALT
      line['qual'] = record.QUAL
      line['filter'] = record.FILTER
      line['format'] = record.FORMAT
      line['info'] = record.INFO
      for s in self.reader.samples:
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
