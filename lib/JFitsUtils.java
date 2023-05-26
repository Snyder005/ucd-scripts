import nom.tam.fits.Fits;
import nom.tam.fits.ImageHDU;
import nom.tam.fits.FitsException;
import nom.tam.fits.Header;
import nom.tam.fits.HeaderCard;
import nom.tam.util.FitsOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.util.Arrays;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.Exception;

public class JFitsUtils {

    public static void reorder_hdus(String infile) throws FileNotFoundException, IOException, FitsException {

        Fits f = new Fits(infile);
        Header prihdr = f.getHDU(0).getHeader();

        String key = new String("HISTORY");
        boolean changed = prihdr.containsKey(key);
        if (changed) {
            return;
        }

        for (int n = 9; n < 13; n++) { 
            
            int m = 25 - n;

            // Get first HDU and make a copy
            ImageHDU hdu1 = (ImageHDU) f.getHDU(n);
            int[][] data1 = (int[][]) hdu1.getKernel();
            int[][] copy1 = new int[data1.length][];
            for (int i = 0; i < data1.length; i++) {
                copy1[i] = Arrays.copyOf(data1[i], data1[i].length);
            }

            // Get second HDU and make a copy
            ImageHDU hdu2 = (ImageHDU) f.getHDU(m);
            int[][] data2 = (int[][]) hdu2.getKernel();
            int[][] copy2 = new int[data2.length][];
            for (int i = 0; i < data2.length; i++) {
                copy2[i] = Arrays.copyOf(data2[i], data2[i].length);
            }

            // Modify first HDU
            for (int i = 0; i < data1.length; i++) {
                for (int j = 0; j < data1[0].length; j++) {
                    data1[i][j] = copy2[i][j];
                }
            }

            // Modify second HDU
            for (int i = 0; i < data2.length; i++) {
                for (int j = 0; j < data2[0].length; j++) {
                    data2[i][j] = copy1[i][j];
                }
            }

            hdu1.rewrite();
            hdu2.rewrite();
        }

        String history = new String("Amp Order Fixed");
        String comment = new String("File modification log.");
        HeaderCard hc = new HeaderCard(key, history, comment);
        prihdr.addLine(hc);
        prihdr.rewrite();

        f.close();

        return;
    }
}
