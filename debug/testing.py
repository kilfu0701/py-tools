from debug import Debug as D

d = D(level=4, color=True)
d.info('this is info')
d.log('this is log')
d.debug('this is debug')
d.error('this is error')

d.info('='*50)

d.log('print multiple item =>', 1, 'string', {'dict': True})


