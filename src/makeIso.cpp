#include "itkImageFileReader.h"
#include "itkImageFileWriter.h"

#include "itkIdentityTransform.h"
#include "itkBSplineInterpolateImageFunction.h"
#include "itkResampleImageFilter.h"

#include "itkXorImageFilter.h"

#include <string>

#include "utils.h"

template<typename TImageType>
typename TImageType::Pointer makeIso(typename TImageType::Pointer inputImage,bool isMask )
{
    typename TImageType::SizeType size = inputImage->GetLargestPossibleRegion().GetSize();
    typename TImageType::SpacingType spacing = inputImage->GetSpacing();

    typename TImageType::SpacingType newSpacing;
    newSpacing[0] = 1;
    newSpacing[1] = 1;
    newSpacing[2] = 1;

    typename TImageType::SizeType newSize;
    newSize[0] = long(size[0] * spacing[0]) + 1;
    newSize[1] = long(size[1] * spacing[1]) + 1;
    newSize[2] = long(size[2] * spacing[2]) + 1;

    auto idTransform = itk::IdentityTransform<double,3>::New();
    auto interpolator = itk::BSplineInterpolateImageFunction<TImageType>::New();

    if( isMask)
    {
        interpolator->SetSplineOrder(0);
    }
    else
    {
        interpolator->SetSplineOrder(3);
    }
    
    auto resampler = itk::ResampleImageFilter<TImageType,TImageType>::New();
    resampler->SetInput(inputImage);
    resampler->SetTransform(idTransform);
    resampler->SetInterpolator(interpolator);
    resampler->SetSize(newSize);
    resampler->SetOutputSpacing(newSpacing);
    resampler->SetOutputOrigin(inputImage->GetOrigin());
    resampler->Update();

    return resampler->GetOutput();
}

int main(int argc,char** argv)
{
    // setting files paths
    std::string patientFileName( argv[1] );
    std::string maskLiverFileName( argv[2] );
    std::string vesselsFileName( argv[3] );
    std::string portalFileName( argv[4] );

    std::string outputPatientFileName( argv[5] );
    std::string outputMaskFileName( argv[6] );
    std::string outputVesselsFileName( argv[7] );

    // settings images types
    using DicomImageType = itk::Image<int16_t,3>;
    using MaskImageType = itk::Image<uint8_t,3>;
    using VesselsImageType = itk::Image<uint8_t,3>;

    // opening files
    auto imgPatient = vUtils::readImage<DicomImageType>(patientFileName,false);
    auto imgMask = vUtils::readImage<MaskImageType>(maskLiverFileName,false);
    auto imgVenacava = vUtils::readImage<VesselsImageType>(vesselsFileName,false);
    auto imgPortal = vUtils::readImage<VesselsImageType>(portalFileName,false);


    // making vessels GT only one image

    auto xorImageFilter = itk::XorImageFilter<VesselsImageType,VesselsImageType>::New();
    xorImageFilter->SetInput1(imgVenacava);
    xorImageFilter->SetInput2(imgPortal);
    xorImageFilter->Update();
    auto imgVessels = xorImageFilter->GetOutput();

    auto imgPatientIso = makeIso<DicomImageType>(imgPatient,false);
    auto imgMaskIso = makeIso<MaskImageType>(imgMask,true);
    auto imgVesselsIso = makeIso<VesselsImageType>(imgVessels,true);
    
    std::cout<<"patient "<<imgPatientIso->GetLargestPossibleRegion().GetSize()<<std::endl;
    std::cout<<"mask "<<imgMaskIso->GetLargestPossibleRegion().GetSize()<<std::endl;
    std::cout<<"vessels "<<imgVesselsIso->GetLargestPossibleRegion().GetSize()<<std::endl;




    using DicomWriterType = itk::ImageFileWriter<DicomImageType>;
    auto writer = DicomWriterType::New();
    writer->SetInput(imgPatientIso );
    writer->SetFileName( outputPatientFileName);
    writer->Update();

    using VesselsWriterType = itk::ImageFileWriter<VesselsImageType>;
    auto vesselsWriter = VesselsWriterType::New();
    vesselsWriter->SetInput(imgVesselsIso );
    vesselsWriter->SetFileName( outputVesselsFileName);
    vesselsWriter->Update();

    using MaskWriterType = itk::ImageFileWriter<MaskImageType>;
    auto maskWriter = MaskWriterType::New();
    maskWriter->SetInput(imgMaskIso );
    maskWriter->SetFileName( outputMaskFileName);
    maskWriter->Update();

    return 0;
}